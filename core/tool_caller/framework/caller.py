from __future__ import annotations

import asyncio
import time
import uuid

from contextvars import ContextVar
from typing import (
    Any,
    Type,
    Coroutine,
    Literal
)

from loguru import logger
from pydantic import BaseModel

from ...context import (
    ContentBlock,
    ContentUnit,
    CallingRequest,
    ToolChoice
)
from .packages import (
    ToolPackage,
    RunningPackage,
    RuntimePackage,
)
from fastapi import Request
from ...global_config_manager import GlobalConfigs
from ...user_config_manager import UserConfigs
from .make_content_result import create_tool_content_unit

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

    forward_call_index: dict[uuid.UUID, set[uuid.UUID]] = {}
    reverse_call_index: dict[uuid.UUID, uuid.UUID] = {}
    call_index_lock = asyncio.Lock()

    _identity: ContextVar[ToolPackage | None] = ContextVar("_identity", default=None)
    _task_id: ContextVar[uuid.UUID | None] = ContextVar("_task_id", default=None)

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
            logger.info(
                "Tool {name} is disabled, skip registration",
                name = package.__name__
            )
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

        logger.info("Register tool {name} done", name = instance.name)
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
                runtime = RuntimePackage(
                    user_id = user_id,
                    tool_call_id = tool_request.id,
                    user_configs = user_configs,
                    global_configs = global_configs,
                    fastapi_request = fastapi_request,
                    loop_times = loop_times,
                    max_loop_times = max_loop_times
                )
                task = asyncio.create_task(
                    coro = cls.run_tool(
                        task_id = task_id,
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
    async def run_tool(
        cls,
        task_id: uuid.UUID,
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
            try:
                parsed_args = tool.parse_params(args)
            except Exception as e:
                return create_tool_content_unit(
                    tool_call_id = runtime.tool_call_id,
                    content = f"Schema validation failed: {str(object = e)}",
                    loop_times = runtime.loop_times,
                    max_loop_times = runtime.max_loop_times
                )

            running = await cls.reg_running(
                task_id = task_id,
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
        except BaseException as e:
            if created is not None:
                created.set_exception(e)
            raise

        result = await running
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
                task_id = task_id,
                start_time = time.time_ns(),
                start_monotonic_time = time.perf_counter_ns(),
                timeout = timeout,
                package = tool,
                args = args,
                task = task
            )
            cls.runnings[task_id] = running
            if runtime.user_id not in cls.running_map:
                cls.running_map[runtime.user_id] = set()
            cls.running_map[runtime.user_id].add(task_id)        
        return running

    @classmethod
    async def enter_tool(
        cls,
        tool: ToolPackage,
        args: BaseModel,
        runtime: RuntimePackage,
    ) -> ContentUnit:
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