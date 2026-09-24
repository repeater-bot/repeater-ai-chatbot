import time
import orjson
import asyncio
import inspect

from fastapi import Request as FastAPI_Request
from typing import (
    Any,
    Literal,
    Type,
    Awaitable,
    Callable,
    TypeVar,
    Generator,
)
from pydantic import BaseModel, ValidationError
from loguru import logger

from ....auxiliary.text import text_content_cutter
from .function import (
    Function
)
from .._function_calling_response import CallingRequest
from .._content_unit import ContentUnit
from .._content_role import ContentRole
from ....user_config_manager import UserConfigs
from ....global_config_manager import ConfigManager
from ._exceptions import JSONDecodeError, ArgumentError
from ._choice import ToolChoice
from ._tool_call_package import ToolCallPackage

T = TypeVar("T")

class FunctionCaller:
    def __init__(self):
        self._functions: dict[str, Function] = {}
        self._already_force_function: bool = False

    def allowed_func(self, available_tool_calls: set[str]) -> Generator[Function, None, None]:
        for name in self._functions:
            function = self._functions.get(name)
            if function is None:
                continue
            if function.name in available_tool_calls:
                yield function
    
    def to_request(self, available_tool_calls: set[str]) -> list[dict[str, Any]]:
        functions: Generator[Function, None, None] = self.allowed_func(available_tool_calls)
        request: list[dict[str, Any]] = [function.struct().model_dump(exclude_none = True) for function in functions]
        return request
    
    def to_choice(self, choice_mode: ToolChoice = ToolChoice.AUTO) -> dict[str, str | dict[str, str]] | Literal["none"] | Literal["auto"] | Literal["required"]:
        match choice_mode:
            case ToolChoice.NONE:
                return ToolChoice.NONE.value
            case ToolChoice.AUTO:
                return ToolChoice.AUTO.value
            case ToolChoice.REQUIRED:
                return ToolChoice.REQUIRED.value
            case ToolChoice.FORCE:
                for function in self._functions.values():
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
    
    def check_force(self):
        for function in self._functions.values():
            if function.force_choice:
                self._already_force_function = True
                return True
        return False
    
    def register_function(self, function: Function):
        if function.force_choice:
            if self._already_force_function:
                raise ValueError("Cannot register more than one force function")
            self._already_force_function = True
        self._functions[function.name] = function
    
    def register_packages(
            self,
            user_id: str,
            packages: list[Type[ToolCallPackage[T]]],
            user_configs: UserConfigs,
            fastapi_request: FastAPI_Request,
            *args,
            **kwargs
        ):
        for package in packages:
            if not issubclass(package, ToolCallPackage):
                raise ValueError("Package must be a subclass of ToolCallPackage")
            package_instance: ToolCallPackage[T] = package(
                user_id = user_id,
                user_configs = user_configs,
                global_configs = ConfigManager.get_configs(),
                fastapi_request = fastapi_request,
                *args,
                **kwargs
            )
            if len(package_instance.Params.model_fields) == 0:
                parameters = None
            else:
                parameters = package_instance.Params
            function: Function[T, BaseModel] = Function(
                name = package_instance.name,
                description = package_instance.get_description(),
                enabled = package_instance.enabled,
                force_choice = package_instance.force_choice,
                callable = package_instance.call, # type: ignore
                json_result = package_instance.json_result,
                call_mode = package_instance.call_mode,
                parameters = parameters,
                on_error = package_instance.on_error,
                on_args_json_decode_error = package_instance.on_args_json_decode_error,
                on_args_validation_error = package_instance.on_args_validation_error,
                on_result_json_encode_error = package_instance.on_result_json_encode_error,
                on_json_result_string_encode_error = package_instance.on_json_result_string_encode_error,
            )
            self.register_function(function)
    
    def unregister_function(self, function_name: str):
        if function_name in self._functions:
            function = self._functions.pop(function_name)
            if function.force_choice:
                self._already_force_function = False
        else:
            raise ValueError(f"Function {function_name} not found")
    
    async def _any_call(self, func: Callable[..., Awaitable[T]] | Callable[..., T] | None, *args, **kwargs) -> T | None:
        if callable(func):
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            elif inspect.isfunction(func):
                return func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
                if inspect.isawaitable(result):
                    return await result
                else:
                    return result
        else:
            return None
    
    async def call_functions(
            self,
            user_id: str,
            calling_requests: list[CallingRequest],
            available_tool_calls: set[str],
            max_concurrent: int = 10
        ) -> list[ContentUnit]:
        results: asyncio.Queue = asyncio.Queue()
        tasks: set[asyncio.Task] = set()
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def _call_function(user_id: str, calling_request: CallingRequest, available_tool_calls: set[str]):
            async with semaphore:
                result = await self.call_function(
                    user_id = user_id,
                    calling_request = calling_request,
                    available_tool_calls = available_tool_calls
                )
                await results.put(result)
        
        for request in calling_requests:
            tasks.add(
                asyncio.create_task(
                    _call_function(
                        user_id = user_id,
                        calling_request = request,
                        available_tool_calls = available_tool_calls
                    )
                )
            )
        
        if tasks:
            await asyncio.gather(*tasks)
        
        results_list: list[ContentUnit] = []
        while not results.empty():
            try:
                results_list.append(results.get_nowait())
            except asyncio.QueueEmpty:
                break
        
        return results_list
    
    def _create_tool_content_unit(self, tool_call_id: str, content: Any) -> ContentUnit:
        return ContentUnit(
            role = ContentRole.TOOL,
            tool_call_id = tool_call_id,
            content = str(content)
        )
    
    async def call_function(
            self,
            user_id: str,
            calling_request: CallingRequest,
            available_tool_calls: set[str]
        ) -> ContentUnit:
        if calling_request.function.name not in available_tool_calls:
            return self._create_tool_content_unit(
                tool_call_id = calling_request.id,
                content = "Error: Function not available."
            )
        try:
            function = self._functions[calling_request.function.name]
        except KeyError:
            return self._create_tool_content_unit(
                tool_call_id = calling_request.id,
                content = "Error: Function not found."
            )
        parameters = function.parameters
        if parameters is not None:
            try:
                arguments = parameters(**orjson.loads(calling_request.function.arguments))
            except orjson.JSONDecodeError as error:
                if function.on_args_json_decode_error:
                    return self._create_tool_content_unit(
                        tool_call_id = calling_request.id,
                        content = await self._any_call(
                            function.on_args_json_decode_error,
                            error
                        )
                    )
                else:
                    raise JSONDecodeError(f"Invalid JSON: {error}") from error
            except ValidationError as error:
                if function.on_args_validation_error:
                    return self._create_tool_content_unit(
                        tool_call_id = calling_request.id,
                        content = await self._any_call(
                            function.on_args_validation_error,
                            error
                        )
                    )
                else:
                    errors = error.errors()
                    buffer: list[str] = []
                    for error_detail in errors:
                        buffer.append(f"{'.'.join(str(i) for i in error_detail['loc'])}: {error_detail['msg']}")
                    raise ArgumentError("\n".join(buffer)) from error
        else:
            arguments = None
        
        logger.info(
            "Calling Tool",
            user_id = user_id
        )

        logger.info(
            "Call Tool Name: {name}(Call Type: {call_type})",
            user_id = user_id,
            name = function.name,
            call_type = function.call_mode.name
        )

        if isinstance(arguments, BaseModel):
            logger.info(
                "Use Arguments:\n{arguments}",
                user_id = user_id,
                arguments = orjson.dumps(arguments.model_dump(), option=orjson.OPT_INDENT_2).decode("utf-8")
            )

        start_time = time.perf_counter_ns()
        try:
            raw_result = await function.call(
                arguments
            )
        finally:
            end_time = time.perf_counter_ns()
            logger.info(
                "Call Tool Time: {time:.3f}ms",
                user_id = user_id,
                time = (end_time - start_time) / 1e6
            )

        if isinstance(raw_result, str):
            result = raw_result
        elif isinstance(raw_result, BaseModel):
            result = orjson.dumps(raw_result.model_dump()).decode("utf-8")
        elif function.json_result:
            try:
                bin_result = orjson.dumps(raw_result)

                try:
                    result = bin_result.decode("utf-8")
                except UnicodeEncodeError as error:
                    result = await self._any_call(
                        function.on_json_result_string_encode_error,
                        bin_result,
                        error
                    )
                
            except orjson.JSONEncodeError as error:
                result = await self._any_call(
                    function.on_result_json_encode_error,
                    error
                )
        else:
            result = str(raw_result)
        
        logger.info(
            "Tool {name} Result:\n{result}",
            user_id = user_id,
            name = function.name,
            result = text_content_cutter(str(result), ConfigManager.get_configs().tool_calls.result_max_length_for_logs)
        )
        
        return self._create_tool_content_unit(
            tool_call_id = calling_request.id,
            content = result
        )
    
    def __contains__(self, item: Any | Function) -> bool:
        if isinstance(item, Function):
            return item.name in self._functions
        else:
            return item in self._functions