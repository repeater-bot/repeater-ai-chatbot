from .._objects import Delta, ToolCall, TokensCount, FinishReason
from ....request_log import Logprob, TopLogprob
from openai.types.chat import ChatCompletionChunk
from openai.types.completion import Completion

async def translation_openai_chunk(
    chunk: ChatCompletionChunk | Completion,
) -> Delta:
    """
    翻译单个OpenAI API响应块

    :param chunk: API响应块
    :return: Delta_data对象
    """
    # 初始化对象
    tokens_usage = TokensCount()
    delta_data = Delta()
    # 转录ID
    if hasattr(chunk, "id"):
        delta_data.id = chunk.id
    # 转录创建时间
    if hasattr(chunk, "created"):
        delta_data.created = chunk.created
    # 转录模型名称
    if hasattr(chunk, "model"):
        delta_data.model = chunk.model
    
    if isinstance(chunk, ChatCompletionChunk):
        # 转录内容
        if hasattr(chunk, "choices") and len(chunk.choices) > 0:
            choice = chunk.choices[0]
            if hasattr(choice, "delta"):
                # 转录推理内容
                if hasattr(choice.delta, "reasoning_content"):
                    reasoning_data = choice.delta.reasoning_content
                    if reasoning_data is not None:
                        delta_data.reasoning_content = reasoning_data

                # 转录响应内容
                if hasattr(choice.delta, "content"):
                    content = choice.delta.content
                    if content:
                        delta_data.content = content
                
                # 转录工具调用
                if hasattr(choice.delta, "tool_calls") and choice.delta.tool_calls:
                    content = choice.delta.tool_calls
                    delta_data.tool_calls = []
                    for call in content:
                        tool_call = ToolCall()
                        if hasattr(call, "id"):
                            tool_call.id = call.id
                        if hasattr(call, "type"):
                            tool_call.type = call.type
                        if hasattr(call, "index") and call.index is not None:
                            tool_call.index = call.index
                        if hasattr(call, "function") and call.function is not None:
                            if hasattr(call.function, "name"):
                                tool_call.name = call.function.name
                            if hasattr(call.function, "arguments"):
                                tool_call.arguments = call.function.arguments
                        delta_data.tool_calls.append(tool_call)
            
            if hasattr(choice, "finish_reason"):
                # 我不知道为什么，这里就是会出现 None
                # 这 很 奇 怪
                # 你这里是明明 Literal["stop", "length", "tool_calls", "content_filter", "function_call"]
                # 为什么会出现 None 呢
                # 你害的我这个 Enum 炸了
                # 所以我要这里加了一个 if
                # 下次记得 Union 上一个 None 吧求了
                # 
                # 2026 前来考古
                # 这里终于在上面写上包含 None 了
                if choice.finish_reason is not None:
                    try:
                        delta_data.finish_reason = FinishReason(choice.finish_reason)
                    except ValueError:
                        delta_data.finish_reason = choice.finish_reason
            
            # 处理logprobs
            if hasattr(choice, "logprobs") and choice.logprobs is not None:
                if hasattr(choice.logprobs, "content") and choice.logprobs.content is not None:
                    logprobs = []
                    for token in choice.logprobs.content:
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

                
        if hasattr(chunk, "system_fingerprint"):
            delta_data.system_fingerprint = chunk.system_fingerprint

        # 转录usage数据
        if hasattr(chunk, "usage") and chunk.usage is not None:
            # 只在最后一个chunk中获取usage数据
            if hasattr(chunk.usage, "prompt_tokens") and chunk.usage.prompt_tokens is not None:
                tokens_usage.prompt_tokens = chunk.usage.prompt_tokens
            if hasattr(chunk.usage, "completion_tokens") and chunk.usage.completion_tokens is not None:
                tokens_usage.completion_tokens = chunk.usage.completion_tokens
            if hasattr(chunk.usage, "total_tokens") and chunk.usage.total_tokens is not None:
                tokens_usage.total_tokens = chunk.usage.total_tokens
            if hasattr(chunk.usage, "prompt_cache_hit_tokens") and chunk.usage.prompt_cache_hit_tokens is not None:
                tokens_usage.prompt_cache_hit_tokens = chunk.usage.prompt_cache_hit_tokens
            if hasattr(chunk.usage, "prompt_cache_miss_tokens") and chunk.usage.prompt_cache_miss_tokens is not None:
                tokens_usage.prompt_cache_miss_tokens = chunk.usage.prompt_cache_miss_tokens
        
        delta_data.token_usage = tokens_usage
    
    elif isinstance(chunk, Completion):
        # 转录ID
        if hasattr(chunk, "id"):
            delta_data.id = chunk.id
        # 转录创建时间
        if hasattr(chunk, "created"):
            delta_data.created = chunk.created
        # 转录模型名称
        if hasattr(chunk, "model"):
            delta_data.model = chunk.model
        
        # 转录内容
        if hasattr(chunk, "choices") and len(chunk.choices) > 0:
            choice = chunk.choices[0]
            if hasattr(choice, "text"):
                delta_data.content = choice.text
            
            if hasattr(choice, "finish_reason"):
                if choice.finish_reason is not None:
                    delta_data.finish_reason = FinishReason(choice.finish_reason)
                
        if hasattr(chunk, "system_fingerprint"):
            delta_data.system_fingerprint = chunk.system_fingerprint

        # 转录usage数据
        if hasattr(chunk, "usage") and chunk.usage is not None:
            # 只在最后一个chunk中获取usage数据
            if hasattr(chunk.usage, "prompt_tokens") and chunk.usage.prompt_tokens is not None:
                tokens_usage.prompt_tokens = chunk.usage.prompt_tokens
            if hasattr(chunk.usage, "completion_tokens") and chunk.usage.completion_tokens is not None:
                tokens_usage.completion_tokens = chunk.usage.completion_tokens
            if hasattr(chunk.usage, "total_tokens") and chunk.usage.total_tokens is not None:
                tokens_usage.total_tokens = chunk.usage.total_tokens
            if hasattr(chunk.usage, "prompt_cache_hit_tokens") and chunk.usage.prompt_cache_hit_tokens is not None:
                tokens_usage.prompt_cache_hit_tokens = chunk.usage.prompt_cache_hit_tokens
            if hasattr(chunk.usage, "prompt_cache_miss_tokens") and chunk.usage.prompt_cache_miss_tokens is not None:
                tokens_usage.prompt_cache_miss_tokens = chunk.usage.prompt_cache_miss_tokens
        
        delta_data.token_usage = tokens_usage

    return delta_data