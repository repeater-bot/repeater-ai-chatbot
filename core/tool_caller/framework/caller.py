from __future__ import annotations

import uuid
import time
import orjson
import asyncio

from contextvars import ContextVar
from typing import (
    Any,
    Type,
    Coroutine,
    Literal
)

from pydantic import BaseModel

from ...user_data_managers.context import (
    ContentBlock,
    ContentUnit,
    CallingRequest,
    ToolChoice
)
from .packages import (
    ToolPackage,
    RunningPackage,
    RuntimePackage,
    IOStreamPackage,
)
from fastapi import Request
from ...global_config_manager import GlobalConfigs
from ...user_data_managers.user_config_manager import UserConfigs
from .make_content_result import create_tool_content_unit
from loguru import logger

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

    runnings: dict[uuid.UUID, RunningPackage] = {}
    running_map: dict[str, set[uuid.UUID]] = {}
    running_lock = asyncio.Lock()

    results: dict[uuid.UUID, RunningPackage] = {}
    result_map: dict[str, set[uuid.UUID]] = {}
    result_lock = asyncio.Lock()

    forward_call_index: dict[uuid.UUID, set[uuid.UUID]] = {}
    reverse_call_index: dict[uuid.UUID, uuid.UUID] = {}
    call_index_lock = asyncio.Lock()

    _identity: ContextVar[ToolPackage | None] = ContextVar("_identity", default=None)
    _task_id: ContextVar[uuid.UUID | None] = ContextVar("_task_id", default=None)

    @classmethod
    async def start(cls) -> None:
        pass

    @classmethod
    async def stop(cls) -> None:
        await cls.close_all_packages()

    @classmethod
    async def close_all_packages(cls) -> None:
        async with cls.running_lock:
            for running in cls.runnings.values():
                running.cancel()
            cls.running = {}
            cls.running_map = {}

        async with cls.result_lock:
            for result in cls.results.values():
                result.cancel()
            cls.results = {}
            cls.result_map = {}

        async with cls.call_index_lock:
            cls.forward_call_index = {}
            cls.reverse_call_index = {}

    @classmethod
    def register(cls, package: Type[ToolPackage]) -> Type[ToolPackage]:
        """
        Register a tool class.

        The tool is instantiated once and then shared by every user and every
        request; anything request scoped travels in the `RuntimePackage` of the
        call instead.

        A tool that sets `enabled = False` is skipped, which is how `Demo` stays
        a debug only tool.

        :param package: The tool class.
        :return: The tool class.
        """
        if not getattr(package, "enabled", True):
            return package

        if package in cls.tools:
            raise ValueError(f"Tool {package.__name__} is already registered")
        if package.name in cls.tool_names:
            raise ValueError(f"Tool name {package.name} is already registered")
        if package.__name__ in cls.class_names:
            raise ValueError(f"Tool class name {package.__name__} is already registered")

        instance = package()
        cls.tools[package] = instance
        cls.tool_names[instance.name] = package
        cls.class_names[package.__name__] = package
        return package

    @classmethod
    def get_tool_names(cls) -> list[str]:
        return list(cls.tool_names.keys())

    @classmethod
    def allowed_tool_ids(cls, allowed: set[str]) -> set[str]:
        return set(cls.tool_names.keys()).intersection(allowed)
    
    @classmethod
    def allowed_tools(cls, allowed: set[str]) -> list[ToolPackage]:
        allowd_tools = cls.allowed_tool_ids(allowed)
        tools: list[ToolPackage] = [cls.tools[cls.tool_names[tool_id]] for tool_id in allowd_tools]
        return tools

    @classmethod
    def to_request(cls, allowed: set[str], strict: bool = False) -> list[dict[str, Any]]:
        """
        To request format.
        """
        return [
            tool.to_request(strict).model_dump()
            for tool in cls.allowed_tools(allowed)
        ]
    
    @classmethod
    def to_choice(cls, choice_mode: ToolChoice = ToolChoice.AUTO) -> dict[str, str | dict[str, str]] | Literal["none", "auto", "required"]:
        match choice_mode:
            case ToolChoice.NONE | ToolChoice.AUTO | ToolChoice.REQUIRED:
                return choice_mode.value
            case ToolChoice.FORCE:
                for function in cls.tools.values():
                    if function.force_choice:
                        return {
                            "type": "function",
                            "function": {
                                "name": function.name,
                            }
                        }
                raise ValueError("No function with force_choice=True found")
            case _:
                raise ValueError(f"Invalid choice mode: {choice_mode}")

    @classmethod
    def match_tool(cls, tool_name: str) -> ToolPackage | None:
        """Match a tool by its name."""
        result = cls.tool_names.get(tool_name)
        if result is not None:
            return cls.tools.get(result)
        return None

    @classmethod
    async def get_runnings(cls, user_id: str) -> list[RunningPackage]:
        """Get the runnings of the user."""
        runnings: list[RunningPackage] = []
        async with cls.running_lock:
            user_runnings = cls.running_map.get(user_id, set())
            for running in user_runnings:
                runnings.append(
                    cls.runnings[running]
                )
        return runnings

    @classmethod
    async def get_running(cls, task_id: uuid.UUID) -> RunningPackage | None:
        """Get the running of the task."""
        async with cls.running_lock:
            if task_id in cls.runnings:
                return cls.runnings[task_id]
            return None
        
    @classmethod
    async def get_result(cls, task_id: uuid.UUID, user_id: str, remove: bool = True) -> RunningPackage | None:
        """Get the result of the task."""
        async with cls.result_lock:
            user_results = cls.result_map.get(user_id, set())
            if task_id in user_results:
                if remove:
                    result = cls.results.pop(task_id, None)
                    if result is not None:
                        user_results.remove(task_id)
                    if not user_results:
                        cls.result_map.pop(user_id, None)
                else:
                    result = cls.results.get(task_id, None)
                return result
        return None

    @classmethod
    async def get_results(cls, user_id: str, remove: bool = True) -> list[RunningPackage]:
        """Get the results of the user."""
        async with cls.result_lock:
            runnings = []
            user_results = cls.result_map.get(user_id, set())
            for task_id in user_results:
                if remove:
                    result = cls.results.pop(task_id, None)
                    if result is not None:
                        runnings.append(result)
                else:
                    result = cls.results.get(task_id)
                    if result is not None:
                        runnings.append(result)
            if remove:
                cls.result_map.pop(user_id, None)
            return runnings

    @classmethod
    async def reset_results(cls, user_id: str):
        """Reset the results of the user."""
        async with cls.result_lock:
            user_results = cls.result_map.pop(user_id, set())
            for result in user_results:
                cls.results.pop(result)

    @classmethod
    async def call_tool(
        cls,
        user_id: str,
        tool_requests: list[CallingRequest],
        user_configs: UserConfigs,
        global_configs: GlobalConfigs,
        available_tool_calls: set[str],
        fastapi_request: Request,
        loop_times: int | None = None,
        max_loop_times: int | None = None
    ) -> list[ContentUnit]:
        """Call a tool with the given arguments."""
        tasks: list[asyncio.Task[ContentUnit]] = []

        for tool_request in tool_requests:
            if tool_request.function.name not in available_tool_calls:
                async def _not_allowed():
                    return create_tool_content_unit(
                        tool_call_id = tool_request.id,
                        content = "Error: Not allowed to call this tool.",
                        loop_times = loop_times,
                        max_loop_times = max_loop_times
                    )
                tasks.append(asyncio.create_task(coro=_not_allowed()))
                continue

            tool = cls.match_tool(tool_request.function.name)
            if tool is None:
                async def _not_found():
                    return create_tool_content_unit(
                        tool_call_id = tool_request.id,
                        content = "Error: Tool not found",
                        loop_times = loop_times,
                        max_loop_times = max_loop_times
                    )
                tasks.append(asyncio.create_task(coro=_not_found()))
            else:
                task_id = uuid.uuid4()
                input_pkg = IOStreamPackage(
                    queue = asyncio.Queue(),
                )
                output_pkg = IOStreamPackage(
                    queue = asyncio.Queue(),
                )
                runtime = RuntimePackage(
                    user_id = user_id,
                    task_id = task_id,
                    tool_call_id = tool_request.id,
                    raw_argument = tool_request.function.arguments,
                    user_configs = user_configs,
                    global_configs = global_configs,
                    fastapi_request = fastapi_request,
                    input = input_pkg,
                    output = output_pkg,
                    loop_times = loop_times,
                    max_loop_times = max_loop_times
                )
                task = asyncio.create_task(
                    coro = cls.run_tool(
                        tool = tool,
                        args = tool_request.function.arguments,
                        runtime = runtime,
                        timeout = None
                    )
                )
                tasks.append(task)

        result = await asyncio.gather(*tasks)
        return result

    @classmethod
    async def _horizontal_call(
        cls,
        task_id: uuid.UUID,
        tool: ToolPackage,
        args: str,
        runtime: RuntimePackage,
        timeout: int | float | None = None,
        created: asyncio.Future[RunningPackage] | None = None,
    ) -> ContentUnit:
        try:
            source_task_id = cls._task_id.get()
            identity = cls._identity.get()
            if source_task_id is None or identity is None:
                raise RuntimeError("Is not a valid tool context.")

            async with cls.call_index_lock:
                childs = cls.forward_call_index.setdefault(source_task_id, set())
                childs.add(task_id)

                cls.reverse_call_index[task_id] = source_task_id
            
            input_pkg = IOStreamPackage(
                queue = asyncio.Queue(),
            )
            output_pkg = IOStreamPackage(
                queue = asyncio.Queue(),
            )
            runtime = RuntimePackage(
                user_id = runtime.user_id,
                task_id = task_id,
                tool_call_id = runtime.tool_call_id,
                raw_argument = args,
                user_configs = runtime.user_configs,
                global_configs = runtime.global_configs,
                fastapi_request = runtime.fastapi_request,
                input = input_pkg,
                output = output_pkg,
                loop_times = runtime.loop_times,
                max_loop_times = runtime.max_loop_times
            )
            try:
                result = await cls.run_tool(
                    tool = tool,
                    args = args,
                    runtime = runtime,
                    timeout = timeout,
                    created = created,
                )
            finally:
                async with cls.call_index_lock:
                    childs = cls.forward_call_index.get(source_task_id)
                    if childs is not None:
                        childs.discard(task_id)
                        if not childs:
                            cls.forward_call_index.pop(source_task_id)
                    cls.reverse_call_index.pop(task_id, None)
            return result
        except BaseException as e:
            if created is not None:
                created.set_exception(e)
            raise

    @classmethod
    async def horizontal_call(
        cls,
        tool: str | Type[ToolPackage] | ToolPackage,
        args: str,
        runtime: RuntimePackage,
        timeout: int | float | None = None,
    ) -> ContentUnit:
        """
        From a tool, call an other tool horizontally, and return the result.
        
        :param tool: The tool to call.
        :param args: The arguments to pass to the tool.
        :param runtime: The runtime to use.
        :param timeout: The timeout for the call.
        :param created: The future to set when the call is created.
        """
        if isinstance(tool, str):
            tool_instance = cls.match_tool(tool)
            if tool_instance is None:
                raise ValueError(f"Tool {tool} not found")
        elif isinstance(tool, type) and issubclass(tool, ToolPackage):
            tool_instance = tool()
        elif isinstance(tool, ToolPackage):
            tool_instance = tool
        else:
            raise TypeError("tool must be a string, a ToolPackage subclass, or a ToolPackage instance")

        task_id = uuid.uuid4()
        result = await cls._horizontal_call(
            task_id,
            tool = tool_instance,
            args = args,
            runtime = runtime,
            timeout = timeout,
        )

        return result

    @classmethod
    async def horizontal_create(
        cls,
        tool: str | Type[ToolPackage] | ToolPackage,
        args: str,
        runtime: RuntimePackage,
        timeout: int | float | None = None,
    ) -> RunningPackage:
        """
        Create a new horizontal call.
        
        :param tool: The tool to call.
        :param args: The arguments to pass to the tool.
        :param runtime: The runtime to use.
        :param timeout: The timeout for the call.
        :param created: The future to set when the call is created.
        """
        if isinstance(tool, str):
            tool_instance = cls.match_tool(tool)
            if tool_instance is None:
                raise ValueError(f"Tool {tool} not found")
        elif isinstance(tool, type) and issubclass(tool, ToolPackage):
            tool_instance = tool()
        elif isinstance(tool, ToolPackage):
            tool_instance = tool
        else:
            raise TypeError("tool must be a string, a ToolPackage subclass, or a ToolPackage instance")

        task_id: uuid.UUID = uuid.uuid4()
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        created: asyncio.Future[RunningPackage] = loop.create_future()
        task: asyncio.Task[ContentUnit] = asyncio.create_task(
            coro = cls._horizontal_call(
                task_id,
                tool = tool_instance,
                args = args,
                runtime = runtime,
                timeout = timeout,
                created = created,
            )
        )

        result = await created
        return result

    @classmethod
    async def run_tool(
        cls,
        tool: ToolPackage,
        args: str,
        runtime: RuntimePackage,
        timeout: int | float | None = None,
        created: asyncio.Future[RunningPackage] | None = None,
    ) -> ContentUnit:
        """
        Run a tool with the given arguments.
        """
        try:
            logger.info(
                "Calling {tool_name} with args: {args}",
                tool_name = tool.name,
                args = args,
            )
            try:
                parsed_args = tool.parse_params(args)
            except Exception as e:
                return create_tool_content_unit(
                    tool_call_id = runtime.tool_call_id,
                    content = f"Schema validation failed: {str(object = e)}",
                    loop_times = runtime.loop_times,
                    max_loop_times = runtime.max_loop_times
                )

            running: RunningPackage = await cls.reg_running(
                task_id = runtime.task_id,
                tool = tool,
                args = parsed_args,
                runtime = runtime,
                coroutine = cls.enter_tool(
                    tool,
                    args = parsed_args,
                    runtime = runtime,
                ),
                timeout = timeout,
            )
            if created is not None:
                created.set_result(running)
            try:
                result = await running
            finally:
                await cls.unreg_running(task_id = runtime.task_id)
            logger.info(
                "Tool {tool} finished with result {result}",
                tool = tool.name,
                result = orjson.dumps(
                    result.to_content(),
                    option = orjson.OPT_INDENT_2
                ).decode(encoding="utf-8"),
            )
        except BaseException as e:
            if created is not None:
                created.set_exception(e)
            raise
        return result

    @classmethod
    async def reg_running(
        cls,
        task_id: uuid.UUID,
        tool: ToolPackage,
        args: BaseModel,
        runtime: RuntimePackage,
        coroutine: Coroutine[None, None, ContentUnit],
        timeout: int | float | None = None
    ) -> RunningPackage:
        """Register a running tool."""
        async with cls.running_lock:
            task = asyncio.create_task(
                coro = coroutine
            )
            running = RunningPackage(
                task_id = runtime.task_id,
                start_time = time.time_ns(),
                start_monotonic_time = time.perf_counter_ns(),
                timeout = timeout,
                package = tool,
                runtime = runtime,
                args = args,
                task = task
            )
            cls.runnings[task_id] = running
            if runtime.user_id not in cls.running_map:
                cls.running_map[runtime.user_id] = set()
            cls.running_map[runtime.user_id].add(task_id)        
        return running

    @classmethod
    async def unreg_running(cls, task_id: uuid.UUID) -> None:
        """Unregister a running tool."""
        async with cls.running_lock:
            if task_id in cls.runnings:
                running = cls.runnings.pop(task_id)
                user_runnings = cls.running_map.get(running.runtime.user_id)
                if user_runnings is not None:
                    user_runnings.remove(task_id)
                    if len(user_runnings) == 0:
                        cls.running_map.pop(running.runtime.user_id)
                async with cls.result_lock:
                    cls.results[running.task_id] = running
                    cls.result_map.setdefault(running.runtime.user_id, set()).add(running.task_id)

    @classmethod
    async def enter_tool(
        cls,
        tool: ToolPackage,
        args: BaseModel,
        runtime: RuntimePackage,
    ) -> ContentUnit:
        cls._identity.set(tool)
        cls._task_id.set(runtime.task_id)
        result = await cls._enter_tool(
            tool = tool,
            args = args,
            runtime = runtime
        )

        parsed_result: ContentUnit = tool.parse_result(
            result,
            tool_call_id = runtime.tool_call_id,
            loop_times = runtime.loop_times,
            max_loop_times = runtime.max_loop_times
        )
        return parsed_result

    @classmethod
    async def _enter_tool(
        cls,
        tool: ToolPackage,
        args: BaseModel,
        runtime: RuntimePackage,
    ) -> Any:
        try:
            result = await tool.call(
                args = args,
                runtime = runtime
            )
            return result
        except BaseException as e:
            return tool.on_error(e)