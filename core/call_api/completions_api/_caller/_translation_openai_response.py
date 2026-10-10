from openai.types.chat import ChatCompletion
from openai.types.completion import Completion
from typing import TextIO
from ....user_data_managers.context import (
    ContentUnit,
)
from .._objects import (
    Request,
    Runtime,
    Response,
    FinishReason,
    ToolCall,
    TokensCount
)
from ....request_log import (
    Logprob,
    TopLogprob,
)

def translation_openai_response(
    request: Request,
    runtime: Runtime,
    response: ChatCompletion | Completion,
    print_file: TextIO
) -> Response:
    model_response = runtime.response
    # 创建响应内容单元
    model_response_content_unit:ContentUnit = ContentUnit()
    # 设置角色
    model_response_content_unit.role = request.output_role
    # chunk计数
    chunk_count:int = 0
    # 空chunk计数
    empty_chunk_count:int = 0
    print_file.write("\n")
    print_file.flush()

    # 处理响应基础信息
    if hasattr(response, "id"):
        model_response.id = response.id
    
    # 写入响应创建时间
    if hasattr(response, "created"):
        model_response.created = response.created
    
    # 写入模型名称
    if hasattr(response, "model"):
        model_response.model = response.model
    
    # 写入系统指纹
    if hasattr(response, "system_fingerprint"):
        model_response.system_fingerprint = response.system_fingerprint
    
    # 处理响应内容
    if hasattr(response, "choices"):
        choices = response.choices[0]
        # 写入完成原因
        if hasattr(choices, "finish_reason"):
            try:
                model_response.finish_reason = FinishReason(choices.finish_reason)
            except ValueError:
                model_response.finish_reason = choices.finish_reason
        
        # 写入内容
        if hasattr(choices, "message"):
            # 处理推理内容
            if hasattr(choices.message, "reasoning_content"):
                model_response_content_unit.reasoning_content = choices.message.reasoning_content
                print_file.write(f"\n\n\033[7m{model_response_content_unit.reasoning_content}\033[0m")
                print_file.flush()
            
            # 处理输出内容
            if hasattr(choices.message, "content"):
                model_response_content_unit.content = choices.message.content
                print_file.write(f"\n\n{model_response_content_unit.content}\n\n")
                print_file.flush()
            
            # 处理工具调用
            if hasattr(choices.message, "tool_calls") and choices.message.tool_calls is not None:
                for call in choices.message.tool_calls:
                    tool_call = ToolCall()
                    # 处理调用函数
                    if hasattr(call, "id"):
                        tool_call.id = call.id
                    if hasattr(call, "type"):
                        tool_call.type = call.type
                    if hasattr(call, "function"):
                        if hasattr(call.function, "name"):
                            tool_call.name = call.function.name
                        if hasattr(call.function, "arguments"):
                            tool_call.arguments = call.function.arguments
                            print_file.write(f"\n\n\033[104m{tool_call.arguments}\033[0m\n\n")
                            print_file.flush()
                    model_response.tool_calls.append(tool_call)
    
    # 处理logprobs
    if hasattr(choices, "logprobs"):
        if hasattr(choices.logprobs, "content"):
            logprobs = []
            for token in choices.logprobs.content:
                logprob = Logprob()
                if hasattr(token, "token"):
                    logprob.token = token.token
                if hasattr(token, "logprob"):
                    logprob.logprob = token.logprob
                if hasattr(token, "top_logprob"):
                    top_logprobs = []
                    for top_token in token.top_logprob:
                        top_logprob = TopLogprob()
                        if hasattr(top_token, "token"):
                            top_logprob.token = top_token.token
                        if hasattr(top_token, "logprob"):
                            top_logprob.logprob = top_token.logprob
                        top_logprobs.append(top_logprob)
                    logprob.top_logprobs = top_logprobs
                logprobs.append(logprob)
            logprobs = logprobs
    
    # 处理usage数据
    model_response.token_usage = TokensCount()
    if hasattr(response, "usage") and response.usage is not None:
        if hasattr(response.usage, "prompt_tokens") and response.usage.prompt_tokens is not None:
            model_response.token_usage.prompt_tokens = response.usage.prompt_tokens
        if hasattr(response.usage, "completion_tokens") and response.usage.completion_tokens is not None:
            model_response.token_usage.completion_tokens = response.usage.completion_tokens
        if hasattr(response.usage, "total_tokens") and response.usage.total_tokens is not None:
            model_response.token_usage.total_tokens = response.usage.total_tokens
        if hasattr(response.usage, "prompt_cache_hit_tokens") and response.usage.prompt_cache_hit_tokens is not None:
            model_response.token_usage.prompt_cache_hit_tokens = response.usage.prompt_cache_hit_tokens
        if hasattr(response.usage, "prompt_cache_miss_tokens") and response.usage.prompt_cache_miss_tokens is not None:
            model_response.token_usage.prompt_cache_miss_tokens = response.usage.prompt_cache_miss_tokens

    print_file.write("\n\n")

    # 添加日志统计数据
    model_response.request_log.id = model_response.id
    model_response.request_log.total_chunk = chunk_count
    model_response.request_log.empty_chunk = empty_chunk_count
    model_response.request_log.total_tokens = model_response.token_usage.total_tokens
    model_response.request_log.prompt_tokens = model_response.token_usage.prompt_tokens
    model_response.request_log.completion_tokens = model_response.token_usage.completion_tokens
    model_response.request_log.cache_hit_count = model_response.token_usage.prompt_cache_hit_tokens
    model_response.request_log.cache_miss_count = model_response.token_usage.prompt_cache_miss_tokens

    # 添加上下文
    model_response.historical_context = request.context
    model_response.new_context.append(model_response_content_unit)

    return model_response