from __future__ import annotations

import asyncio
import time
import uuid

from contextvars import ContextVar, Token
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Type,
)

from loguru import logger

from ...context import (
    CallingRequest,
    ContentBlock,
    ContentUnit,
    ToolChoice,
)
from .exceptions import (
    ToolArgsError,
    ToolContextError,
)
from .make_content_result import create_tool_content_unit
from .output import Output
from .packages import (
    ToolPackage,
    RunningPackage,
    LetterPackage,
    PipePackage,
    StatusPackage,
    ParamsPackage
)
from .tool_context import (
    ToolContext,
    reset_context,
    set_context,
)

if TYPE_CHECKING:
    from fastapi import Request as FastAPI_Request

    from ...user_config_manager import UserConfigs

ToolReturn = int | None
ToolContent = str | list[ContentBlock]


class ToolsCaller:
    """
    The registry and the dispatcher of every tool of the process.

    The registry is process wide: a tool class is registered once and is then
    shared by every user and every request. Anything request scoped is carried
    by the `ToolContext` of the tool call instead.
    """

    tools: dict[Type[ToolPackage], ToolPackage] = {}
    tool_names: dict[str, Type[ToolPackage]] = {}
    class_names: dict[str, Type[ToolPackage]] = {}
    _force_choice: Type[ToolPackage] | None = None

    runnings: dict[uuid.UUID, RunningPackage] = {}
    running_map: dict[str, set[uuid.UUID]] = {}
    running_lock = asyncio.Lock()

    variables: dict[str, str] = {}
    variable_lock = asyncio.Lock()

    letters_listener: dict[uuid.UUID, LetterPackage[Any]] = {}
    letters_listener_map: dict[str, dict[str, uuid.UUID]] = {}
    letters_listener_lock: asyncio.Lock = asyncio.Lock()

    pipes: dict[uuid.UUID, PipePackage[Any, Any]] = {}
    pipe_map: dict[str, dict[str, uuid.UUID]] = {}
    pipe_lock: asyncio.Lock = asyncio.Lock()

    statuses: dict[uuid.UUID, StatusPackage] = {}
    statuses_map: dict[str, dict[str, uuid.UUID]] = {}
    status_lock: asyncio.Lock = asyncio.Lock()

    forward_call_index: dict[uuid.UUID, set[uuid.UUID]] = {}
    reverse_call_index: dict[uuid.UUID, uuid.UUID] = {}
    call_index_lock = asyncio.Lock()

    _identity: ContextVar[ToolPackage | None] = ContextVar("_identity", default=None)
    _task_id: ContextVar[uuid.UUID | None] = ContextVar("_task_id", default=None)

    # ------------------------------------------------------------------ #
    # Registry
    # ------------------------------------------------------------------ #

    @classmethod
    def match_tool(cls, string: str) -> Type[ToolPackage]:
        """
        Resolve a tool name to its tool class.

        :param string: The name of the tool, as the model sees it.
        :return: The tool class.
        :raises KeyError: If no tool carries that name.
        """
        return cls.tool_names[string]

    @classmethod
    def get_instance(cls, package: Type[ToolPackage]) -> ToolPackage:
        """
        Get the instance of a registered tool.

        :param package: The tool class.
        :return: The tool instance.
        """
        return cls.tools[package]

    @classmethod
    def allowed_tools(cls, available_tool_calls: set[str] | None = None) -> Generator[ToolPackage, None, None]:
        """
        Iterate over the tool instances a caller is allowed to use.

        :param available_tool_calls: The allowed tool names, every tool is yielded when omitted.
        :return: The tool instances.
        """
        for name, package_class in cls.tool_names.items():
            if available_tool_calls is not None and name not in available_tool_calls:
                continue
            package_instance = cls.tools.get(package_class)
            if package_instance is None:
                continue
            yield package_instance

    @classmethod
    def to_request(cls, available_tool_calls: set[str] | None = None, strict: bool = False) -> list[dict[str, Any]]:
        """
        Build the `tools` payload of a model request.

        :param available_tool_calls: The allowed tool names, every tool is included when omitted.
        :param strict: Whether the model API should enforce the schema strictly.
        :return: The tool declarations.
        """
        return [
            package.struct(strict = strict).model_dump(exclude_none = True)
            for package in cls.allowed_tools(available_tool_calls)
        ]

    @classmethod
    def to_choice(
        cls,
        choice_mode: ToolChoice = ToolChoice.AUTO
    ) -> dict[str, str | dict[str, str]] | str:
        """
        Build the `tool_choice` payload of a model request.

        :param choice_mode: The requested choice mode.
        :return: The choice payload.
        """
        match choice_mode:
            case ToolChoice.NONE:
                return ToolChoice.NONE.value
            case ToolChoice.AUTO:
                return ToolChoice.AUTO.value
            case ToolChoice.REQUIRED:
                return ToolChoice.REQUIRED.value
            case ToolChoice.FORCE:
                package = cls._force_choice
                if package is None:
                    raise ValueError("No tool with force_choice=True is registered")
                return {
                    "type": "function",
                    "function": {
                        "name": cls.get_instance(package).package_name,
                    }
                }
            case _:
                raise ValueError(f"Invalid choice mode: {choice_mode}")

    @classmethod
    def register(
        cls,
        package: Type[ToolPackage]
    ) -> Type[ToolPackage]:
        """
        Register a tool.

        :param package: The tool class.
        :return: The tool class.
        """
        return cls._register(package)

    @classmethod
    def register_with_args(
        cls,
        *args,
        **kwargs
    ) -> Callable[[Type[ToolPackage]], Type[ToolPackage]]:
        """
        Register a tool with constructor arguments.

        :param args: args
        :param kwargs: kwargs
        :return: a decorator that registers a tool with args
        """
        def _decorator(package: Type[ToolPackage]) -> Type[ToolPackage]:
            """
            Register a tool with args

            WARNING: This is a decorator, so if you get this function, pass a tool class into it.
            It will pass the data to the registry through the closure.

            :param package: The tool class.
            :return: The tool class.
            """
            nonlocal args, kwargs
            return cls._register(package, *args, **kwargs)
        return _decorator

    @classmethod
    def _register(cls, package: Type[ToolPackage], *args: Any, **kwargs: Any) -> Type[ToolPackage]:
        """
        Register a tool.

        :param package: The tool class.
        :return: The tool class.
        """
        if not package.enabled:
            logger.info(
                "Tool {name} is disabled, skip registration",
                name = package.__name__
            )
            return package

        register_start_time = time.perf_counter_ns()
        try:
            package_instance = cls._make_pack(package, *args, **kwargs)
        except BaseException as e:
            logger.error(
                "Tool {name} failed to register: {error}",
                name = package.__name__,
                error = e
            )
            package.on_reg_failed(e)
            return package

        cls._reg_package_instance(
            package = package,
            package_instance = package_instance
        )
        package_instance.__post_init__()
        package_instance.__time_for_registered__ = time.time_ns()
        register_end_time = time.perf_counter_ns()
        package_instance.__time_for_registered_monotonic__ = register_end_time

        logger.info(
            "Register tool {name} done, cost {cost:.3f} ms",
            name = package_instance.package_name,
            cost = (register_end_time - register_start_time) / 1e6
        )
        return package

    @classmethod
    def _make_pack(
        cls,
        package: Type[ToolPackage],
        *args: Any,
        **kwargs: Any,
    ) -> ToolPackage:
        """
        Make a tool instance.

        :param package: The tool class.
        :param args: The tool class initialization parameters.
        :param kwargs: The tool class initialization parameters.
        :return: The tool instance.
        """
        package_raw_new = package.__new__

        def package_new(cls: Type[ToolPackage], *args: Any, **kwargs: Any):
            # `type.__call__` hands the constructor arguments to `__new__` as
            # well as to `__init__`, so they have to be accepted (and ignored)
            # here; otherwise `register_with_args` fails with a TypeError.
            nonlocal package_raw_new
            package_instance = package_raw_new(cls)
            package_instance.__pre_init__()
            return package_instance

        package.__new__ = package_new
        package.__raw_new__ = package_raw_new

        package_instance = package(*args, **kwargs)
        package_instance.__time_for_created__ = time.time_ns()
        package_instance.__time_for_created_monotonic__ = time.perf_counter_ns()

        return package_instance

    @classmethod
    def _reg_package_instance(
        cls,
        package: Type[ToolPackage],
        package_instance: ToolPackage,
    ) -> None:
        """
        Register a tool instance.

        :param package: The tool class.
        :param package_instance: The tool instance.
        """
        cls._reg_package(
            package = package,
            package_instance = package_instance
        )
        package_instance.on_registed()

    @classmethod
    def _unreg_package_instance(
        cls,
        package: Type[ToolPackage],
    ) -> ToolPackage:
        """
        Unregister a tool instance.

        :param package: The tool class.
        :return: The tool instance.
        """
        package_instance = cls.tools.pop(package)
        cls.tool_names.pop(package_instance.package_name, None)
        cls.class_names.pop(package.__name__, None)

        if cls._force_choice is package:
            cls._force_choice = None

        return package_instance

    @classmethod
    def _reg_package(
        cls,
        package: Type[ToolPackage],
        package_instance: ToolPackage
    ) -> None:
        """
        Register a tool instance into the resource pool.

        :param package: The tool class.
        :param package_instance: The tool instance.
        """
        if package in cls.tools:
            package_instance.on_duplicate_type()

        if package_instance.package_name in cls.tool_names:
            package_instance.on_duplicate_package_name(
                cls.tool_names[package_instance.package_name]
            )

        if package.__name__ in cls.class_names:
            package.on_duplicate_class_name(
                cls.class_names[package.__name__]
            )

        if package_instance.force_choice:
            other = cls._force_choice
            if other is not None and other is not package:
                raise ValueError(
                    f"Tool {package_instance.package_name} and "
                    f"{cls.tools[other].package_name} both declare force_choice=True"
                )
            cls._force_choice = package

        cls.tools[package] = package_instance
        cls.tool_names[package_instance.package_name] = package
        cls.class_names[package.__name__] = package

    @classmethod
    def reset(cls) -> None:
        """
        Forget every registered tool.

        Intended for tests and for reloading a package.
        """
        cls.tools.clear()
        cls.tool_names.clear()
        cls.class_names.clear()
        cls._force_choice = None

    @classmethod
    def registed_info_table(cls) -> Generator[str, None, None]:
        """
        Get registed info table
        """
        total = len(cls.tools)
        yield f"Registed {total} tools"

        types: dict[str, list[ToolPackage]] = {}
        for package in cls.tools.values():
            types.setdefault(package.package_type, []).append(package)

        for package_type, packages in types.items():
            yield f"  {package_type}({len(packages) / total:.2%})"
            for package_instance in packages:
                yield f"    {package_instance.package_name}"

    @classmethod
    def log_registed_info(cls) -> None:
        """
        Log registed info
        """
        for info in cls.registed_info_table():
            logger.info(
                "{info}",
                info = info
            )

    @classmethod
    def destroy(cls, package: Type[ToolPackage]) -> None:
        """
        Destroy a tool.

        :param package: The tool class.
        """
        if package in cls.tools:
            package_instance = cls._unreg_package_instance(package)

            logger.info(
                "Destroy tool: {name}",
                name = package_instance.package_name
            )

            package_instance.on_destroy()

    @classmethod
    async def adestroy(cls, package: Type[ToolPackage]) -> None:
        """
        Destroy a tool on an async context.

        :param package: The tool class.
        """
        if package in cls.tools:
            package_instance = cls._unreg_package_instance(package)

            logger.info(
                "Async destroy tool: {name}",
                name = package_instance.package_name
            )

            await package_instance.on_adestroy()

    # ------------------------------------------------------------------ #
    # Dispatch
    # ------------------------------------------------------------------ #

    @classmethod
    async def _load_user_configs(cls, user_id: str) -> UserConfigs:
        """
        Load the configs of a user, falling back to the defaults.

        :param user_id: The user id.
        :return: The user configs.
        """
        from ...runtime_container import RuntimeContainer
        from ...user_config_manager import UserConfigs

        try:
            runtime = RuntimeContainer.get_runtime()
            return await runtime.user_config_manager.load(
                user_id = user_id
            )
        except Exception as error:
            logger.warning(
                "Could not load the configs of user {user_id}, using defaults: {error}",
                user_id = user_id,
                error = error
            )
            return UserConfigs()

    @classmethod
    async def call_tools(
        cls,
        user_id: str,
        tool_calls: list[CallingRequest],
        available_tool_calls: set[str] | None = None,
        user_configs: UserConfigs | None = None,
        fastapi_request: FastAPI_Request | None = None,
        max_concurrent: int = 10,
        loop_times: int | None = None,
        max_loop_times: int | None = None,
        timeout: int | float | None = None,
    ) -> list[ContentUnit]:
        """
        Run every tool call of one model response and collect their responses.

        The responses come back in the order the calls were made in.

        :param user_id: The user the calls belong to.
        :param tool_calls: The tool calls of the model response.
        :param available_tool_calls: The allowed tool names, every tool is allowed when omitted.
        :param user_configs: The configs of the user, loaded when omitted.
        :param fastapi_request: The request that started the generation loop.
        :param max_concurrent: The amount of tool calls that may run at once.
        :param loop_times: The current generation round.
        :param max_loop_times: The generation round limit.
        :param timeout: The timeout of every single tool call.
        :return: One tool response per tool call.
        """
        if not tool_calls:
            return []

        context = ToolContext(
            user_id = user_id,
            user_configs = user_configs,
            fastapi_request = fastapi_request,
        )
        if context.user_configs is None:
            context.user_configs = await cls._load_user_configs(user_id)

        semaphore = asyncio.Semaphore(max_concurrent)

        async def _call(tool_call: CallingRequest) -> ContentUnit:
            async with semaphore:
                return await cls.call_tool(
                    tool_call = tool_call,
                    context = context,
                    available_tool_calls = available_tool_calls,
                    loop_times = loop_times,
                    max_loop_times = max_loop_times,
                    timeout = timeout,
                )

        return list(
            await asyncio.gather(
                *(_call(tool_call) for tool_call in tool_calls)
            )
        )

    @classmethod
    async def call_tool(
        cls,
        tool_call: CallingRequest,
        context: ToolContext,
        available_tool_calls: set[str] | None = None,
        loop_times: int | None = None,
        max_loop_times: int | None = None,
        timeout: int | float | None = None,
    ) -> ContentUnit:
        """
        Run one tool call and build its response.

        :param tool_call: The tool call of the model response.
        :param context: The context of the call.
        :param available_tool_calls: The allowed tool names, every tool is allowed when omitted.
        :param loop_times: The current generation round.
        :param max_loop_times: The generation round limit.
        :param timeout: The timeout of the tool call.
        :return: The tool response.
        """
        name = tool_call.function.name

        def _error(message: str) -> ContentUnit:
            return create_tool_content_unit(
                tool_call_id = tool_call.id,
                content = message,
                loop_times = loop_times,
                max_loop_times = max_loop_times,
            )

        if available_tool_calls is not None and name not in available_tool_calls:
            return _error("Error: Function not available.")

        package_class = cls.tool_names.get(name)
        if package_class is None:
            return _error("Error: Function not found.")

        package_instance = cls.tools[package_class]
        output = Output()

        try:
            parsed_args = await package_instance.parse_args(
                tool_call.function.arguments
            )
        except ToolArgsError as error:
            return _error(str(error))

        params = ParamsPackage.build(
            user_id = context.user_id,
            args = parsed_args,
            tool_call_id = tool_call.id,
            output = output,
            loop_times = loop_times,
            max_loop_times = max_loop_times,
        )

        await cls.run_handle(
            user_id = context.user_id,
            task_id = uuid.uuid4(),
            package = package_instance,
            args = params,
            timeout = timeout,
            context = context,
        )

        return create_tool_content_unit(
            tool_call_id = tool_call.id,
            content = await output.to_tool_response(),
            loop_times = loop_times,
            max_loop_times = max_loop_times,
        )

    @classmethod
    async def invoke(
        cls,
        user_id: str,
        package: Type[ToolPackage] | ToolPackage,
        args: Any,
        user_configs: UserConfigs | None = None,
        fastapi_request: FastAPI_Request | None = None,
        tool_call_id: str = "",
        loop_times: int | None = None,
        max_loop_times: int | None = None,
        timeout: int | float | None = None,
    ) -> tuple[ToolReturn, ToolContent]:
        """
        Run a tool directly, without a model tool call.

        This is the entry point for callers that already hold typed arguments:
        cron jobs, the chat core, or a test.

        :param user_id: The user the call belongs to.
        :param package: The tool class or instance.
        :param args: The parsed arguments of the tool.
        :param user_configs: The configs of the user, loaded when omitted.
        :param fastapi_request: The request that started the generation loop.
        :param tool_call_id: The id to report the call under.
        :param loop_times: The current generation round.
        :param max_loop_times: The generation round limit.
        :param timeout: The timeout of the call.
        :return: The return code of the tool and the content it produced.
        """
        if isinstance(package, ToolPackage):
            package_instance = package
        elif isinstance(package, type) and issubclass(package, ToolPackage):
            registered = cls.tools.get(package)
            package_instance = registered if registered is not None else package()
        else:
            raise TypeError("package must be a ToolPackage or a subclass of ToolPackage")

        if user_configs is None:
            user_configs = await cls._load_user_configs(user_id)

        context = ToolContext(
            user_id = user_id,
            user_configs = user_configs,
            fastapi_request = fastapi_request,
        )
        output = Output()
        params = ParamsPackage.build(
            user_id = user_id,
            args = args,
            tool_call_id = tool_call_id,
            output = output,
            loop_times = loop_times,
            max_loop_times = max_loop_times,
        )

        code = await cls.run_handle(
            user_id = user_id,
            task_id = uuid.uuid4(),
            package = package_instance,
            args = params,
            timeout = timeout,
            context = context,
        )

        return code, await output.to_tool_response()

    @classmethod
    async def run_handle(
        cls,
        user_id: str,
        task_id: uuid.UUID,
        package: ToolPackage,
        args: ParamsPackage,
        created: asyncio.Future[RunningPackage] | None = None,
        timeout: int | float | None = None,
        context: ToolContext | None = None,
    ) -> ToolReturn:
        """
        Run a tool and track it while it runs.

        :param user_id: The user the call belongs to.
        :param task_id: The id of the call.
        :param package: The tool instance.
        :param args: The params of the call.
        :param created: A future that receives the running package as soon as it exists.
        :param timeout: The timeout of the call.
        :param context: The context to run the call in, the ambient one is inherited when omitted.
        :return: The return code of the tool.
        """
        try:
            task = asyncio.create_task(
                cls.enter_handler(
                    task_id = task_id,
                    package = package,
                    args = args,
                    timeout = timeout,
                    context = context,
                )
            )
            running: RunningPackage = RunningPackage(
                task_id = task_id,
                start_time = time.time_ns(),
                start_monotonic_time = time.perf_counter_ns(),
                timeout = timeout,
                package = package,
                args = args,
                task = task
            )

            async with cls.running_lock:
                cls.runnings[task_id] = running
                cls.running_map.setdefault(
                    user_id,
                    set()
                ).add(task_id)
        except Exception as e:
            if created is not None:
                created.set_exception(e)
            raise

        if created is not None:
            created.set_result(running)

        try:
            result = await running
            return result
        finally:
            async with cls.running_lock:
                cls.runnings.pop(task_id, None)
                if user_id in cls.running_map:
                    user_running = cls.running_map[user_id]
                    user_running.discard(task_id)
                    if not user_running:
                        cls.running_map.pop(user_id, None)

    @classmethod
    async def enter_handler(
        cls,
        task_id: uuid.UUID,
        package: ToolPackage,
        args: ParamsPackage,
        timeout: int | float | None = None,
        context: ToolContext | None = None,
    ) -> ToolReturn:
        """
        Enter the tool handler.

        :param task_id: The task id.
        :param package: The tool package.
        :param args: The params package.
        :param timeout: The timeout of the tool handler.
        :param context: The context to enter, the ambient one is inherited when omitted.
        :return: The result of the tool handler.
        """
        context_token: Token[ToolContext | None] | None = None
        if context is not None:
            context_token = set_context(context)

        identity_token = cls._identity.set(package)
        task_token = cls._task_id.set(task_id)

        try:
            result = await cls._enter_handler(
                task_id = task_id,
                package = package,
                args = args,
                timeout = timeout,
            )
        finally:
            cls._task_id.reset(task_token)
            cls._identity.reset(identity_token)
            if context_token is not None:
                reset_context(context_token)

        logger.info(
            "Handler {handler}[{task_id}] return code: {retvalue}",
            handler = package.package_name,
            task_id = task_id,
            retvalue = result or "none"
        )
        return result

    @classmethod
    async def _enter_handler(
        cls,
        task_id: uuid.UUID,
        package: ToolPackage,
        args: ParamsPackage,
        timeout: int | float | None = None,
    ) -> ToolReturn:
        """
        Enter the tool handler.

        :param task_id: The task id.
        :param package: The tool package.
        :param args: The params package.
        :param timeout: The timeout of the tool handler.
        :return: The result of the tool handler.
        """
        try:
            logger.info(
                "Enter {tool}[{task_id}]",
                tool = package.package_name,
                task_id = task_id,
            )

            task = asyncio.create_task(
                coro = package.enter_handler(
                    args = args
                )
            )
            return await asyncio.wait_for(
                task,
                timeout = timeout,
            )

        except asyncio.CancelledError:
            return await package.on_cancel(args)
        except asyncio.TimeoutError:
            return await package.on_timeout(args)
        except Exception as e:
            return await package.on_error(e, args)
        except BaseException as e:
            return await package.on_interpreter_error(e, args)
        finally:
            await package.handler_exit(args)

    @classmethod
    async def _horizontal_enter(
        cls,
        user_id: str,
        task_id: uuid.UUID,
        package: ToolPackage,
        args: ParamsPackage,
        timeout: int | float | None = None,
        created: asyncio.Future[RunningPackage] | None = None
    ) -> ToolReturn:
        now_task_id = cls._task_id.get()
        identity = cls._identity.get()
        if now_task_id is None or identity is None:
            raise RuntimeError(f"This interface is not used in the {cls.__name__} context.")

        async with cls.call_index_lock:
            childs = cls.forward_call_index.setdefault(now_task_id, set())
            childs.add(task_id)

            cls.reverse_call_index[task_id] = now_task_id

        logger.info(
            "Horizontal Enter {handler}({task_id}) -> {sub_handler}({sub_task_id})",
            handler = identity.package_name,
            task_id = now_task_id,
            sub_handler = package.package_name,
            sub_task_id = task_id
        )

        try:
            return await cls.run_handle(
                user_id = user_id,
                task_id = task_id,
                package = package,
                args = args,
                timeout = timeout,
                created = created
            )
        finally:
            async with cls.call_index_lock:
                childs = cls.forward_call_index.get(now_task_id)
                if childs is not None:
                    childs.discard(task_id)
                    if not childs:
                        cls.forward_call_index.pop(now_task_id, None)
                cls.reverse_call_index.pop(task_id, None)

    @classmethod
    def _resolve_package(cls, package: Type[ToolPackage] | ToolPackage) -> ToolPackage:
        """
        Resolve a tool class or instance to its registered instance.

        :param package: The tool class or instance.
        :return: The tool instance.
        """
        if isinstance(package, ToolPackage):
            return package
        elif isinstance(package, type) and issubclass(package, ToolPackage):
            return cls.get_instance(package)
        else:
            raise TypeError("package must be a ToolPackage or a subclass of ToolPackage")

    @classmethod
    async def horizontal_call(
        cls,
        user_id: str,
        package: Type[ToolPackage] | ToolPackage,
        args: ParamsPackage,
        timeout: int | float | None = None,
    ) -> ToolReturn:
        """
        Call another tool from inside a running tool.

        The call inherits the context of the caller, so the callee sees the same
        user and the same request.

        :param user_id: The user the call belongs to.
        :param package: The tool class or instance.
        :param args: The params of the call.
        :param timeout: The timeout of the call.
        :return: The return code of the call.
        """
        return await cls._horizontal_enter(
            user_id = user_id,
            task_id = uuid.uuid4(),
            package = cls._resolve_package(package),
            args = args,
            timeout = timeout
        )

    @classmethod
    async def horizontal_enter_wait_created(
        cls,
        user_id: str,
        package: Type[ToolPackage] | ToolPackage,
        args: ParamsPackage,
        timeout: int | float | None = None,
    ) -> RunningPackage:
        """
        Call another tool from inside a running tool and wait for it to be tracked.

        :param user_id: The user the call belongs to.
        :param package: The tool class or instance.
        :param args: The params of the call.
        :param timeout: The timeout of the call.
        :return: The running package of the call.
        """
        task_id = uuid.uuid4()
        loop = asyncio.get_running_loop()
        created: asyncio.Future[RunningPackage] = loop.create_future()
        asyncio.create_task(
            coro = cls._horizontal_enter(
                user_id = user_id,
                task_id = task_id,
                package = cls._resolve_package(package),
                args = args,
                timeout = timeout,
                created = created
            )
        )
        return await created

    # ------------------------------------------------------------------ #
    # Running tasks
    # ------------------------------------------------------------------ #

    @classmethod
    async def get_task_id(cls) -> uuid.UUID:
        """
        Get the id of the tool call that is running in the current context.

        :return: The task id.
        """
        task_id = cls._task_id.get()
        if task_id is None:
            raise ToolContextError(f"This interface is not used in the {cls.__name__} context.")
        return task_id

    @classmethod
    async def has_running_task(cls, user_id: str, task: uuid.UUID) -> bool:
        """
        Check if a task is running.

        :param user_id: user id
        :param task: task
        :return: True if task is running, False otherwise
        """
        async with cls.running_lock:
            return task in cls.running_map.get(user_id, set())

    @classmethod
    async def get_runnings(cls, user_id: str) -> set[RunningPackage]:
        """
        Get running tasks.

        :param user_id: user id
        :return: set of running tasks
        """
        async with cls.running_lock:
            runnings = cls.running_map.get(user_id, set())
            return {cls.runnings[i] for i in runnings if i in cls.runnings}

    @classmethod
    async def get_running_ids(cls, user_id: str) -> set[uuid.UUID]:
        """
        Get running tasks.

        :param user_id: user id
        :return: set of running tasks
        """
        async with cls.running_lock:
            runnings = cls.running_map.get(user_id, set())
            return {i for i in runnings if i in cls.runnings}

    @classmethod
    async def get_running(cls, user_id: str, task_id: uuid.UUID) -> RunningPackage | None:
        """
        Get running task.

        :param user_id: user id
        :param task_id: task id
        :return: running task
        """
        async with cls.running_lock:
            runnings = cls.running_map.get(user_id, set())
            if task_id not in runnings:
                return None
            return cls.runnings[task_id]

    # ------------------------------------------------------------------ #
    # Letters
    # ------------------------------------------------------------------ #

    @classmethod
    async def create_letters(cls, user_id: str, name: str) -> LetterPackage:
        """
        Create a letters package.

        Replacing a letters package that is still waiting cancels the old one.

        :param user_id: The user id.
        :param name: The name of the letters package.
        :return: The letters package.
        """
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        sponsor = cls._task_id.get()
        if sponsor is None:
            raise ToolContextError(f"This interface is not used in the {cls.__name__} context.")

        letters_id = uuid.uuid4()
        letters_package = LetterPackage(
            future = future,
            name = name,
            id = letters_id,
            sponsor = sponsor,
        )

        async with cls.letters_listener_lock:
            user_letters = cls.letters_listener_map.setdefault(user_id, {})
            previous_id = user_letters.get(name)
            if previous_id is not None:
                previous = cls.letters_listener.pop(previous_id, None)
                if previous is not None and not previous.done():
                    previous.cancel()

            user_letters[name] = letters_id
            cls.letters_listener[letters_id] = letters_package

        return letters_package

    @classmethod
    async def submit_letters(cls, user_id: str, name: str, value: Any) -> bool:
        """
        Submit a letters.

        :param user_id: The user id.
        :param name: The name of the letters.
        :param value: The value to hand to the waiting letters package.
        :return: Whether the submit is successful.
        """
        async with cls.letters_listener_lock:
            user_letters = cls.letters_listener_map.get(user_id)
            if user_letters is None:
                return False

            letters_ids = user_letters.get(name)
            if letters_ids is None:
                return False

            letters_packages = cls.letters_listener.get(letters_ids)
            if letters_packages is None or letters_packages.done():
                return False

            user_letters.pop(name, None)
            if not user_letters:
                cls.letters_listener_map.pop(user_id, None)
            cls.letters_listener.pop(letters_ids, None)

            letters_packages.set_result(value)
            return True

    # ------------------------------------------------------------------ #
    # Pipes
    # ------------------------------------------------------------------ #

    @classmethod
    async def open_pipe(cls, user_id: str, name: str) -> PipePackage[Any, Any]:
        """
        Open a pipe package.

        :param user_id: The user id.
        :param name: The name of the pipe package.
        :return: The pipe package.
        """
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        sponsor = cls._task_id.get()
        if sponsor is None:
            raise ToolContextError(f"This interface is not used in the {cls.__name__} context.")

        pipe_id = uuid.uuid4()
        pipe_package = PipePackage(
            upstream = asyncio.Queue(),
            downstream = future,
            name = name,
            sponsor = sponsor,
            id = pipe_id,
        )

        async with cls.pipe_lock:
            user_pipes = cls.pipe_map.setdefault(user_id, {})
            if name in user_pipes:
                other_pipe_id = user_pipes[name]
                other_pipe = cls.pipes[other_pipe_id]
                if other_pipe.opened():
                    raise RuntimeError("The pipe is already opened.")
                other_pipe.downstream.set_result(pipe_package.upstream)
                pipe_package.downstream.set_result(other_pipe.upstream)
                other_pipe.other_id = pipe_id
                pipe_package.other_id = other_pipe_id
            else:
                user_pipes[name] = pipe_id
            cls.pipes[pipe_id] = pipe_package

        return pipe_package

    @classmethod
    async def close_pipe(cls, user_id: str, name: str) -> bool:
        """
        Close a pipe package.

        :param user_id: The user id.
        :param name: The name of the pipe package.
        :return: Whether the close is successful.
        """
        async with cls.pipe_lock:
            user_pipes = cls.pipe_map.get(user_id)
            if user_pipes is None:
                return False

            pipe_id = user_pipes.pop(name, None)
            if pipe_id is None:
                return False
            if not user_pipes:
                cls.pipe_map.pop(user_id, None)

            pipe_package = cls.pipes.pop(pipe_id, None)
            if pipe_package is None:
                return False
            await pipe_package.close()

            other_pipe_id = pipe_package.other_id
            if other_pipe_id is None:
                return True

            other_pipe = cls.pipes.pop(other_pipe_id, None)
            if other_pipe is not None:
                await other_pipe.close()
            return True

    # ------------------------------------------------------------------ #
    # Statuses
    # ------------------------------------------------------------------ #

    @classmethod
    async def create_status(cls, user_id: str, name: str) -> StatusPackage:
        """
        Create a status package.

        Replacing a status that is still waiting cancels the old one.

        :param user_id: The user id.
        :param name: The name of the status package.
        :return: The status package.
        """
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        sponsor = cls._task_id.get()
        if sponsor is None:
            raise ToolContextError(f"This interface is not used in the {cls.__name__} context.")

        status_id = uuid.uuid4()
        status_package = StatusPackage(
            future = future,
            status_id = status_id,
            sponsor = sponsor
        )

        async with cls.status_lock:
            user_statuses = cls.statuses_map.setdefault(user_id, {})
            previous_id = user_statuses.get(name)
            if previous_id is not None:
                previous = cls.statuses.pop(previous_id, None)
                if previous is not None and not previous.is_finished():
                    previous.cancel()

            user_statuses[name] = status_id
            cls.statuses[status_id] = status_package

        return status_package

    @classmethod
    async def wait_status(cls, user_id: str, name: str) -> None:
        """
        Wait a status.

        :param user_id: The user id.
        :param name: The name of the status.
        """
        async with cls.status_lock:
            user_statuses = cls.statuses_map.get(user_id)
            if user_statuses is None:
                raise RuntimeError("The namespace is not found.")
            status_id = user_statuses.get(name)
            if status_id is None:
                raise RuntimeError("The status is not found.")
            status_package = cls.statuses[status_id]
        await status_package.wait_finish()

    @classmethod
    async def finish_status(cls, user_id: str, name: str) -> bool:
        """
        Finish a status.

        :param user_id: The user id.
        :param name: The name of the status.
        :return: Whether the finish is successful.
        """
        async with cls.status_lock:
            user_statuses = cls.statuses_map.get(user_id)
            if user_statuses is None:
                return False
            status_id = user_statuses.pop(name, None)
            if status_id is None:
                return False
            if not user_statuses:
                cls.statuses_map.pop(user_id, None)
            status_package = cls.statuses.pop(status_id, None)
            if status_package is None:
                return False
            status_package.finish()
            return True

    # ------------------------------------------------------------------ #
    # Shutdown
    # ------------------------------------------------------------------ #

    @classmethod
    async def close_packages(cls):
        """
        Close all packages.
        """
        async with cls.running_lock:
            for runnings in cls.runnings.values():
                runnings.cancel()

            cls.runnings = {}
            cls.running_map = {}

        async with cls.letters_listener_lock:
            for letter in cls.letters_listener.values():
                letter.cancel()

            cls.letters_listener = {}
            cls.letters_listener_map = {}

        async with cls.pipe_lock:
            for pipe in cls.pipes.values():
                await pipe.close()

            cls.pipes = {}
            cls.pipe_map = {}

        async with cls.status_lock:
            for status in cls.statuses.values():
                status.cancel()

            cls.statuses = {}
            cls.statuses_map = {}

        async with cls.call_index_lock:
            cls.forward_call_index = {}
            cls.reverse_call_index = {}
