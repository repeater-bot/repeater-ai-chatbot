import asyncio

from ..context import (
    Context,
    Function,
    FunctionCaller,
    CallingRequest,
    ContentUnit,
    ToolChoice,
    ToolCallPackage
)
from ..call_api.completions_api import (
    StreamClient,
    NoStreamClient,
    Request,
    Response,
    Runtime,
    Delta,
    APIConnectionError,
    InternalServerError
)
from ..clients.model_info import (
    ModelsClient,
    ModelInfo
)
from ..user_config_manager import UserConfigs
from ..global_config_manager import GlobalConfigs
from typing import (
    AsyncGenerator,
    ClassVar,
    Type
)
from loguru import logger
from fastapi import Request as FastAPI_Request
from ._exceptions import *
from ..special_exception import HTTPException
from ._multi_response import MultiResponse

class ModelRequester:
    _global_package: ClassVar[list[Type[ToolCallPackage]]] = []
    def __init__(
            self,
            user_id: str,
            user_configs: UserConfigs,
            global_configs: GlobalConfigs,
            fastapi_request: FastAPI_Request,
            model_info_client: ModelsClient,
            max_concurrency: int | None = None,
            *args, **kwargs
        ):
        self._tools_caller = FunctionCaller()
        self._tools_caller.register_packages(
            user_id = user_id,
            packages = self._global_package,
            user_configs = user_configs,
            fastapi_request = fastapi_request,
            *args,
            **kwargs
        )
        self._api_client = NoStreamClient(
            global_configs.callapi.max_concurrency
            if max_concurrency is None else max_concurrency
        )
        self._stream_api_client = StreamClient(
            global_configs.callapi.max_concurrency
            if max_concurrency is None else max_concurrency
        )
        self._user_configs = user_configs
        self._global_configs = global_configs
        self._model_info_client = model_info_client
        self._stream_chunk_queue: asyncio.Queue[Delta | ContentUnit | None] = asyncio.Queue()
        self._tool_responses: list[list[ContentUnit]] = []
    
    @classmethod
    def reg_global_package(cls, package: Type[ToolCallPackage]):
        if not issubclass(package, ToolCallPackage):
            raise TypeError("package must be a subclass of ToolCallPackage")
        cls._global_package.append(package)
        return package
    
    def reg_func(self, function: Function):
        self._tools_caller.register_function(function)
    
    def reg_packages(
            self,
            user_id: str,
            packages: list[Type[ToolCallPackage]],
            user_configs: UserConfigs,
            fastapi_request: FastAPI_Request
        ):
        self._tools_caller.register_packages(
            user_id = user_id,
            packages = packages,
            user_configs = user_configs,
            fastapi_request = fastapi_request
        )
    
    def unreg_func(self, func_name: str):
        self._tools_caller.unregister_function(func_name)
    
    @property
    def tools_caller(self) -> FunctionCaller:
        return self._tools_caller
    
    @tools_caller.setter
    def tools_caller(self, tools_caller: FunctionCaller):
        if not isinstance(tools_caller, FunctionCaller):
            raise TypeError("tools_caller must be a FunctionCaller")
        self._tools_caller = tools_caller
    
    async def generator(self) -> AsyncGenerator[Delta | ContentUnit, None]:
        failed_times: int = 0
        while True:
            try:
                delta = await asyncio.wait_for(self._stream_chunk_queue.get(), 10)
            except asyncio.TimeoutError:
                failed_times += 1
                if failed_times > 5:
                    break
            if delta is None:
                break
            yield delta
    
    async def _parse_response(
            self,
            request: Request,
            response: Response,
            runtime: Runtime,
            available_tool_calls: set[str] | None = None,
        ) -> None:
        if available_tool_calls and response.tool_calls:
            with runtime.status_stack.enter("Calling Tools"):
                calling_requests: list[CallingRequest] = []
                for tool_call in response.tool_calls:
                    calling_requests.append(
                        tool_call.to_calling_request()
                    )
                results = await self._tools_caller.call_functions(
                    response.user_id,
                    calling_requests = calling_requests,
                    available_tool_calls = available_tool_calls,
                )
                self._tool_responses.append(results)
                for tool_response in results:
                    await self._stream_chunk_queue.put(tool_response)
                if request.context:
                    request.context.extend(response.new_context)
                else:
                    request.context = response.new_context
                request.context.extend(results)
                
                if not request.tool_calling_remove_reasoning:
                    request.remove_reasoning_prompt = False
                    
                response.new_context.clear()
                raise Regenerate(request)
    
    async def submit(
        self,
        user_id:str,
        request: Request,
        runtime: Runtime,
        max_generated_times: int = 16,
        available_tool_calls: set[str] | None = None,
        tool_choice_model: ToolChoice = ToolChoice.AUTO,
        stream: bool = False,
    ) -> MultiResponse:
        generated_times: int = 0
        responses: MultiResponse = MultiResponse()
        if request.context is None:
            historical_context = Context()
        else:
            historical_context = request.context.copy()
        responses.historical_context = historical_context.copy()
        remove_reasoning_prompt = request.remove_reasoning_prompt
        if request.remove_reasoning_prompt:
            submit_context = historical_context.remove_reasoning_content()
        else:
            submit_context = request.context
        request.context = submit_context
        if available_tool_calls and max_generated_times > 1:
            logger.info(
                "Using tools: {tools}",
                user_id = user_id,
                tools = ", ".join(
                    func.name for func in self._tools_caller.allowed_func(available_tool_calls)
                )
            )
            request.tools = self._tools_caller.to_request(available_tool_calls)
            request.tool_choice = self._tools_caller.to_choice(tool_choice_model)
        try:
            while True:
                try:
                    generated_times += 1
                    logger.info(
                        "Generate Times: {now}/{max}",
                        user_id = user_id,
                        now = generated_times,
                        max = max_generated_times
                    )
                    response = await self._send_request(
                        user_id = user_id,
                        request = request,
                        runtime = runtime,
                        stream = stream
                    )
                    responses.add_copy(response)
                    responses.tool_requests = self._tool_responses
                    await self._parse_response(
                        request = request,
                        response = response,
                        runtime = runtime,
                        available_tool_calls = available_tool_calls,
                    )
                    raise GenerateFinished
                except Regenerate as e:
                    logger.info(
                        "Regenerate",
                        user_id = user_id,
                    )
                    request = e.request
                    runtime.content_buffer.clear()
                    if generated_times >= max_generated_times:
                        raise GenerateFinished
                    elif (generated_times + 1) >= max_generated_times:
                        logger.warning(
                            "Times too many, removeing tools",
                            user_id = user_id,
                        )
                        request.tools = None
                        request.tool_choice = None
        except GenerateFinished as e:
            logger.info(
                "GenerateFinished",
                user_id = user_id,
            )
            runtime.content_buffer.clear()
            return responses
        finally:
            request.remove_reasoning_prompt = remove_reasoning_prompt
    
    async def _send_request(
        self,
        user_id: str,
        request: Request,
        runtime: Runtime,
        stream: bool = False,
    ) -> Response:
        try:
            if stream:
                async def send_chunk(delta: Delta):
                    await self._stream_chunk_queue.put(delta)
                
                response = await self._stream_api_client.submit_request(
                    user_id = user_id,
                    request = request,
                    runtime = runtime,
                    chunk_callback = send_chunk
                )
            else:
                response = await self._api_client.submit_request(
                    user_id = user_id,
                    request = request,
                    runtime = runtime
                )

            return response
        except (APIConnectionError, InternalServerError) as e:
            logger.error(
                "{error_type}: {error_message}",
                error_type = type(e).__name__,
                error_message = e.message,
            )
            await self._model_info_client.disable(
                model_id = request.model_uid,
                timeout = int(self._global_configs.callapi.failed_disable_timeout * 1e9)
            )
            model = await self._model_info_client.get_random_model(
                model_id = request.model_id
            )
            self.update_request_model(request, model)
            raise Regenerate(request) from e

    def update_request_model(self, request: Request, model: ModelInfo) -> None:
        request.url = model.get_base_url()
        request.model = model.id
        request.model_uid = model.uid
        request.limits = model.limits
        request.timeout = model.timeout
        if self._user_configs.model_timeout is None:
            request.timeout = model.timeout
        else:
            request.timeout = self._user_configs.model_timeout
        if model.api_key is not None:
            request.key = model.api_key
        else:
            raise HTTPException(
                status_code = 403,
                detail = "No api key for model",
            )