from ...runtime_container import RuntimeContainer
from ..framework import ToolsCaller, ToolPackage, RuntimePackage
from ...request_log import RequestLog
from pydantic import BaseModel

@ToolsCaller.register
class TokenCount(ToolPackage):
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

    async def call(self, args: Params, runtime: RuntimePackage):
        request_log_manager = RuntimeContainer.get_runtime().request_log
        request_logs = request_log_manager.read_stream_request_log()

        total_tokens = 0
        input_tokens = 0
        output_tokens = 0
        cache_hit_count = 0
        cache_miss_count = 0

        async for request_log in request_logs:
            if isinstance(request_log, RequestLog):
                if request_log.user_id == runtime.user_id:
                    # NOTE: the old implementation accumulated into
                    # `total_token_count` / `input_token_count` /
                    # `output_token_count`, which are never defined anywhere in
                    # the module, so this branch raised NameError as soon as the
                    # first log of the user was read.
                    total_tokens += request_log.total_tokens or 0
                    input_tokens += request_log.prompt_tokens or 0
                    output_tokens += request_log.completion_tokens or 0
                    if request_log.cache_hit_count or request_log.cache_miss_count:
                        cache_hit_count += request_log.cache_hit_count or 0
                        cache_miss_count += request_log.cache_miss_count or 0
                    else:
                        cache_miss_count += request_log.prompt_tokens or 0

        cache_total = cache_hit_count + cache_miss_count
        return self.Result(
            total_tokens = total_tokens,
            input_tokens = input_tokens,
            output_tokens = output_tokens,
            cache_hit_count = cache_hit_count,
            cache_miss_count = cache_miss_count,
            # NOTE: the old implementation divided unconditionally, so a user
            # without a single log got a ZeroDivisionError instead of a ratio.
            cache_hit_ratio = cache_hit_count / cache_total if cache_total else 0.0
        )
