from ...context import ToolCallPackage, CallMode
from ...runtime_container import RuntimeContainer
from .._caller import ModelRequester
from ...request_log import RequestLog
from pydantic import BaseModel

@ModelRequester.reg_global_package
class TokenCount(ToolCallPackage):
    class Params(BaseModel):
        pass

    class Result(BaseModel):
        total_tokens: int
        input_tokens: int
        output_tokens: int
        cache_hit_count: int
        cache_miss_count: int
        cache_hit_ratio: float

    name = "token_count"
    description = "Calculates the total Token consumption for the current user."
    call_mode = CallMode.ASYNC

    async def call(self, args: Params):
        runtime = RuntimeContainer.get_runtime()
        request_log_manager = runtime.request_log
        request_logs = request_log_manager.read_stream_request_log()

        total_tokens = 0
        input_tokens = 0
        output_tokens = 0
        cache_hit_count = 0
        cache_miss_count = 0

        async for request_log in request_logs:
            if isinstance(request_log, RequestLog):
                if request_log.user_id == self.user_id:
                    total_token_count += request_log.total_tokens or 0
                    input_token_count += request_log.prompt_tokens or 0
                    output_token_count += request_log.completion_tokens or 0
                    if request_log.cache_hit_count or request_log.cache_miss_count:
                        cache_hit_count += request_log.cache_hit_count or 0
                        cache_miss_count += request_log.cache_miss_count or 0
                    else:
                        cache_miss_count += request_log.prompt_tokens or 0
        
        return self.Result(
            total_tokens = total_tokens,
            input_tokens = input_tokens,
            output_tokens = output_tokens,
            cache_hit_count = cache_hit_count,
            cache_miss_count = cache_miss_count,
            cache_hit_ratio = cache_hit_count / (cache_hit_count + cache_miss_count)
        )