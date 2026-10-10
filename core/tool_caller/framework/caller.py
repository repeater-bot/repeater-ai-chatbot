import sys
import time
import uuid
import asyncio
from datetime import datetime
from typing import (
    Any,
    Type,
    Callable,
    Awaitable,
    TypeVar,
    Union,
    NoReturn,
    Generator
)
from .packages import (
    ToolPackage,
    RunningPackage,
    LetterPackage,
    PipePackage,
    StatusPackage,
    ParamsPackage
)
from ...auxiliary.text import text_content_cutter
from ...context import ContentUnit
from .output import Output
from contextvars import ContextVar
from loguru import logger

T_Handler_Result = TypeVar("T_Handler_Result")

class ToolsCaller:
    tools: dict[Type[ToolPackage], ToolPackage] = {}
    tool_names: dict[str, Type[ToolPackage]] = {}
    class_names: dict[str, Type[ToolPackage]] = {}

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

    @classmethod
    async def get_task_id(cls) -> uuid.UUID:
        """
        Get task id.

        :return: task id
        """
        task_id = cls._task_id.get()
        if task_id is None:
            raise RuntimeError(f"This interface is not used in the {cls.__name__} context.")
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

    @classmethod
    def match_tool(cls, string: str) -> Type[ToolPackage]:
        """
        Use the string to match the tool.

        Query triggers if an initiator is used.
        If not, the component is queried.

        :param string: trigger or component
        :return: command package
        """
        return cls.tool_names[string]
    
    @classmethod
    def get_instance(cls, package: Type[ToolPackage]) -> ToolPackage:
        """
        Get the instance of the command package.

        :param package: The command package.
        :return: The instance of the command package.
        """
        return cls.tools[package]

    @classmethod
    async def create_letters(cls, user_id: str, name: str) -> LetterPackage:
        """
        Create a letters package.

        :param user_id: The user id.
        :param name: The name of the letters package.
        :return: The letters package.
        """
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        sponsor = cls._task_id.get()
        if sponsor is None:
            raise RuntimeError(f"This interface is not used in the {cls.__name__} context.")

        letters_id = uuid.uuid4()
        letters_package = LetterPackage(
            future = future,
            name = name,
            id = letters_id,
            sponsor = sponsor,
        )

        async with cls.letters_listener_lock:
            user_letters = cls.letters_listener_map.setdefault(user_id, {})
            user_letters[name] = letters_id
            cls.letters_listener[letters_id] = letters_package

        return letters_package

    @classmethod
    async def submit_letters(cls, user_id: str, name: str, value: Any) -> bool:
        """
        Submit a letters.

        :param user_id: The user id.
        :param name: The name of the letters.
        :param letters_package: The letters package.
        :return: Whether the submit is successful.
        """
        async with cls.letters_listener_lock:
            user_letters = cls.letters_listener_map.get(user_id)
            if user_letters is None:
                return False

            letters_ids = user_letters.pop(name, None)
            if letters_ids is None:
                return False

            if not user_letters:
                cls.letters_listener_map.pop(user_id)

            letters_packages = cls.letters_listener.pop(letters_ids)
            letters_packages.set_result(value)
            return True

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
            raise RuntimeError(f"This interface is not used in the {cls.__name__} context.")

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
                if other_pipe.opened:
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
                cls.pipe_map.pop(user_id)
            
            pipe_package = cls.pipes.pop(pipe_id)
            await pipe_package.close()

            other_pipe_id = pipe_package.other_id
            if other_pipe_id is None:
                return True
            
            other_pipe = cls.pipes.pop(other_pipe_id)
            await other_pipe.close()
            return True

    @classmethod
    async def create_status(cls, user_id: str, name: str) -> StatusPackage:
        """
        Create a status package.

        :param user_id: The user id.
        :param name: The name of the status package.
        :return: The status package.
        """
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        sponsor = cls._task_id.get()
        if sponsor is None:
            raise RuntimeError(f"This interface is not used in the {cls.__name__} context.")

        status_id = uuid.uuid4()
        status_package = StatusPackage(
            future = future,
            status_id = status_id,
            sponsor = sponsor
        )

        async with cls.status_lock:
            user_statuses = cls.statuses_map.setdefault(user_id, {})
            user_statuses[name] = status_id
            cls.statuses[status_id] = status_package

        return status_package

    @classmethod
    async def wait_status(cls, user_id: str, name: str) -> None:
        """
        Wait a status.

        :param user_id: The user id.
        :param name: The name of the status.
        :return: The status.
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
                cls.statuses_map.pop(user_id)
            status_package = cls.statuses.pop(status_id)
            status_package.finish()
            return True

    @classmethod
    async def run_handle(
        cls,
        user_id: str,
        task_id: uuid.UUID,
        package: ToolPackage,
        args: ParamsPackage,
        created: asyncio.Future[RunningPackage] | None = None,
        timeout: int | float | None = None,
    ) -> int | None:
        try:
            task = asyncio.create_task(
                cls.enter_handler(
                    task_id = task_id,
                    package = package,
                    args = args,
                    timeout = timeout
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
    ) -> int | None:
        """
        Enter the message handler.

        :param task_id: The task id.
        :param package: The tool package.
        :param args: The params package.
        :param timeout: The timeout of the message handler.
        :return: The result of the message handler.
        """

        cls._identity.set(package)
        cls._task_id.set(task_id)
        
        result = await cls._enter_hander(
            task_id = task_id,
            package = package,
            args = args,
            timeout = timeout,
        )

        logger.info(
            "Handler {handler}[{task_id}] return code: {retvalue}",
            handler = package.package_name,
            task_id = task_id,
            retvalue = result or "none"
        )
        return result
    
    @classmethod
    async def _enter_hander(
        cls,
        task_id: uuid.UUID,
        package: ToolPackage,
        args: ParamsPackage,
        timeout: int | float | None = None,
    ) -> int | None:
        """
        Enter the message handler.

        :param task_id: The task id.
        :param package: The command package.
        :param args: The params package.
        :param timeout: The timeout of the message handler.
        :return: The result of the message handler.
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
    ):
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
                        cls.forward_call_index.pop(now_task_id)
                cls.reverse_call_index.pop(task_id, None)
    
    @classmethod
    async def horizontal_call(
        cls,
        user_id: str,
        package: Type[ToolPackage] | ToolPackage,
        args: ParamsPackage,
        timeout: int | float | None = None,
    ) -> int | None:
        """
        Horizontal call handler

        :param package: CommandPackage
        :param persona_info: PersonaInfo
        :param send_msg: SendMsg
        :param debug_mode: run handler at debug mode
        :return: Handler result
        """
        if isinstance(package, ToolPackage):
            package_instance = package
        elif isinstance(package, type) and issubclass(package, ToolPackage):
            package_instance: ToolPackage = cls.get_instance(package)
        else:
            raise TypeError("package must be CommandPackage or subclass of CommandPackage")
        
        task_id = uuid.uuid4()
        return await cls._horizontal_enter(
            user_id = user_id,
            task_id = task_id,
            package = package_instance,
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
        Horizontal call handler and waiting for the running package to created.

        :param package: CommandPackage
        :param persona_info: PersonaInfo
        :param send_msg: SendMsg
        :param debug_mode: DebugMode
        :return: RunningPackage
        """
        if isinstance(package, ToolPackage):
            package_instance = package
        elif isinstance(package, type) and issubclass(package, ToolPackage):
            package_instance: ToolPackage = cls.get_instance(package)
        else:
            raise TypeError("package must be CommandPackage or subclass of CommandPackage")
        
        task_id = uuid.uuid4()
        loop = asyncio.get_running_loop()
        created: asyncio.Future[RunningPackage] = loop.create_future()
        asyncio.create_task(
            coro = cls._horizontal_enter(
                user_id = user_id,
                task_id = task_id,
                package = package_instance,
                args = args,
                timeout = timeout,
                created = created
            )
        )
        return await created

    @classmethod
    def register(
        cls,
        package: Type[ToolPackage]
    ) -> Type[ToolPackage]:
        """
        Register a command

        :param package: CommandPackage
        :return: CommandPackage
        """
        return cls._register(package)

    @classmethod
    def register_with_args(
        cls,
        *args,
        **kwargs
    ) -> Callable[[Type[ToolPackage]], type[ToolPackage]]:
        """
        Register a command with args

        :param args: args
        :param kwargs: kwargs
        :return: a decorator that registers a command with args
        """
        def _decorator(package: Type[ToolPackage]) -> Type[ToolPackage]:
            """
            Register a command with args

            WARNING: This is a decorator, so if you get this function, pass a command class into it.
            It will pass the data to the registry through the closure.

            :param package: CommandPackage
            :return: CommandPackage
            """
            nonlocal args, kwargs
            return cls._register(package, *args, **kwargs)
        return _decorator
    
    @classmethod
    def _register(cls, package: Type[ToolPackage], *args: Any, **kwargs: Any) -> Type[ToolPackage]:
        """
        Register a command

        :param package: CommandPackage Type
        :return: CommandPackage Type
        """
        if package.enabled:
            register_start_time = time.perf_counter_ns()
            try:
                package_instance = cls._make_pack(package, *args, **kwargs)
            except BaseException as e:
                package.on_reg_failed(e)
            
            cls._reg_package_instance(
                package = package,
                package_instance = package_instance
            )
            package_instance.__post_init__()
            package_instance.__time_for_registered__ = time.time_ns()
            register_end_time = time.perf_counter_ns()
            package_instance.__time_for_registered_monotonic__ = register_end_time

            logger.info(
                "Register command {name} done, cost {cost:.3f} ms",
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
    )  -> ToolPackage:
        """
        Make a command package instance

        :param package: Package class
        :param args: Package class initialization parameters
        :param kwargs: Package class initialization parameters
        :return: package_instance, matcher, handler
        """
        package_raw_new = package.__new__

        def package_new(cls: Type[ToolPackage]):
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
        Register a package instance

        :param package: Package class
        :param package_instance: Package instance
        :param matcher: Matcher class
        :param handler: Handler function
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
    ):
        """
        Unregister a package instance

        :param package: Package class
        :return: Package instance and Matcher class
        """
        package_instance = cls.tools.pop(package)
        name = cls.tool_names.pop(package_instance.package_name)
        class_name = cls.tool_names.pop(package_instance.package_name)

        return package_instance

    
    @classmethod
    def _reg_package(
        cls,
        package: Type[ToolPackage],
        package_instance: ToolPackage
    ) -> None:
        """
        Register package to resource pool

        :param package: package class
        :param package_instance: package instance
        :param matcher: matcher class
        """
        if package in cls.tools:
            package_instance.on_duplicate_type()
        cls.tools[package] = package_instance

        if package_instance.package_name in cls.tool_names:
            package_instance.on_duplicate_package_name(
                cls.tool_names[package_instance.package_name]
            )
        cls.tool_names[package_instance.package_name] = package
        
        if package.__name__ in cls.class_names:
            package.on_duplicate_class_name(
                cls.class_names[package.__name__]
            )
        cls.class_names[package.__name__] = package
    
    @classmethod
    def registed_info_table(cls) -> Generator[str, None, None]:
        """
        Get registed info table
        """
        total = len(cls.tools)
        yield f"Registed {total} tools"

        types: dict[str, list[ToolPackage]] = {}
        for package in cls.tools.values():
            if package.package_type not in types:
                types[package.package_type] = []
            types[package.package_type].append(package)
        
        if total > 0:
            yield "Repeater:"
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
        Destroy a Handler

        :param package: The package of the Handler
        """
        if package in cls.tools:
            package_instance = cls._unreg_package_instance(package)

            logger.info(
                "Destroy Handler: {name}",
                name = package_instance.package_name
            )
            
            package_instance.on_destroy()
    
    @classmethod
    async def adestroy(cls, package: Type[ToolPackage]) -> None:
        """
        Destroy a Handler on an async context
        
        :param package: The package of the Handler
        """
        if package in cls.tools:
            package_instance = cls._unreg_package_instance(package)

            logger.info(
                "Async Destroy command: {name}",
                name = package_instance.package_name
            )
            
            await package_instance.on_adestroy()