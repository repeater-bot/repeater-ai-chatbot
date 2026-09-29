import sys
import asyncio

from datetime import datetime
from typing import AsyncGenerator, Self, TextIO
from ._objects import Request, Delta, ToolCall, Response, Runtime
from ...request_log import RequestLog
from ...context import ContentUnit
from ...request_log import TimeStamp
from ...global_config_manager import ConfigManager
from ...logger_init import config_to_log_level, LogLevel
from ...text_buffer import ContentBuffer, TextBuffer
from loguru import logger

class StreamingResponseGenerationLayer:
    """
    Delta 生成流包装器

    用于在流式响应中创建统计夹层以恢复非流式调用时的统计功能

    ---

    :param user_id: 用户ID
    :param request: 请求对象
    :param response_iterator: 原始响应迭代器
    """

    def __init__(
            self,
            user_id: str,
            request: Request,
            runtime: Runtime,
            response_iterator: AsyncGenerator[Delta, None],
            print_file: TextIO = sys.stdout
        ) -> None:


        self.request: Request = request
        self._response_iterator: AsyncGenerator[Delta, None] = response_iterator
        self._finished: bool = False
        self._print_file: TextIO = print_file
        # ==== Initialize the response object ==== #
        
        # 创建响应对象
        self.response = runtime.response

        # 设置用户ID
        self.user_id = user_id

        # 写入调用日志基础信息
        self.response.request_log.url = self.request.url
        self.response.request_log.user_id = self.user_id
        self.response.request_log.user_name = self.request.user_name
        self.response.request_log.model = self.request.model
        self.response.request_log.stream = self.request.stream

        # set tool calls
        self.tool_calls: dict[int, ToolCall] = {}

        # 如果context为空，则抛出异常
        if not self.request.context:
            raise ValueError("context is required")
        
        # chunk计数器
        self.chunk_count:int = 0
        # 空chunk计数器
        self.empty_chunk_count:int = 0

        # 开始处理流式响应
        if self.request.print_chunk:
            self._print_file.write("\n")
            self._print_file.flush()
        # 记录流开始时间
        # 记录上次chunk时间
        self.created:TimeStamp = TimeStamp()
        # chunk耗时列表
        self.chunk_times:list[TimeStamp] = []
        self.processor_queue_backlog: list[int] = []

        self._chunk_queue: asyncio.Queue[Delta | Exception | None] = asyncio.Queue()

        # 文本缓冲区
        self._content_buffer = runtime.content_buffer

        self._print_chunk = config_to_log_level(ConfigManager.get_configs().logger.level) > LogLevel.TRACE
    
    def finally_stream(self):
        stream_processing_end_time: TimeStamp = TimeStamp()
        if self.request.print_chunk:
            self._print_file.write("\n\n")
            self._print_file.flush()

        # 添加日志统计数据
        self.response.request_log.id = self.response.id
        self.response.request_log.total_chunk = self.chunk_count
        self.response.request_log.empty_chunk = self.empty_chunk_count
        self.response.request_log.created_time = self.response.created
        self.response.request_log.chunk_times = self.chunk_times
        self.response.request_log.queue_backlog = self.processor_queue_backlog
        if self.response.token_usage is not None:
            self.response.request_log.total_tokens = self.response.token_usage.total_tokens
            self.response.request_log.prompt_tokens = self.response.token_usage.prompt_tokens
            self.response.request_log.completion_tokens = self.response.token_usage.completion_tokens
            self.response.request_log.cache_hit_count = self.response.token_usage.prompt_cache_hit_tokens
            self.response.request_log.cache_miss_count = self.response.token_usage.prompt_cache_miss_tokens
        self.response.request_log.stream_processing_end_time = stream_processing_end_time
        self.response.request_log.total_context_length = self.response.historical_context.total_length

        # 由于工具调用不分顺序，而是通过 ID 定位
        # 所以这里这里可以忽略索引
        if self.tool_calls:
            for index, buffer in self._content_buffer.tool_calls_arguments_buffer.items():
                self.tool_calls[index].arguments = str(buffer)
        self.response.tool_calls = list(self.tool_calls.values())

        # 添加上下文
        self.model_response_content_unit:ContentUnit = ContentUnit()
        self.model_response_content_unit.role = self.request.output_role
        if self._content_buffer.reasoning_buffer:
            self.model_response_content_unit.reasoning_content = str(self._content_buffer.reasoning_buffer)
        if self._content_buffer:
            self.model_response_content_unit.content = str(self._content_buffer.content_buffer)
        if self.response.tool_calls:
            self.model_response_content_unit.tool_calls = [call.to_calling_request() for call in self.response.tool_calls]
        if not self.request.context:
            raise ValueError("Be must have context")
        self.response.historical_context = self.request.context
        self.response.new_context.append(self.model_response_content_unit)
    
    async def _read_chunk(self):
        try:
            async for chunk in self._response_iterator:
                await self._chunk_queue.put(chunk)
            await self._chunk_queue.put(None)
        except Exception as e:
            await self._chunk_queue.put(e)

    def __aiter__(self) -> Self:
        """
        Returns the streaming response generation layer as an iterator.
        """
        stream_processing_start_time: TimeStamp = TimeStamp()
        self.response.request_log.stream_processing_start_time = stream_processing_start_time
        asyncio.create_task(self._read_chunk())
        return self

    async def __anext__(self) -> Delta:
        """
        Returns the next chunk of data from the streaming response generation layer.
        """
        delta_data = await self._chunk_queue.get()
        self.processor_queue_backlog.append(self._chunk_queue.qsize())
        if delta_data is None:
            if not self._finished:
                self._finished = True
            self.finally_stream()
            raise StopAsyncIteration
        elif isinstance(delta_data, Exception):
            raise delta_data
        else:
            self._parse_delta(delta_data)
            return delta_data

    def _parse_delta(self, delta_data: Delta):
        # 记录会话开启时间
        if not self.response.created:
            self.response.created = delta_data.created
        
        # 记录chunk时间
        this_chunk_time = TimeStamp()
        self.chunk_times.append(this_chunk_time)
        
        # 记录会话ID
        if not self.response.id:
            self.response.id = delta_data.id
        
        # 记录模型名称
        if not self.response.model:
            self.response.model = delta_data.model
        
        # 记录token使用情况
        if delta_data.token_usage:
            self.response.token_usage = delta_data.token_usage

        # 记录模型推理响应内容
        if delta_data.reasoning_content:
            if self.request.print_chunk:
                if not self._content_buffer.reasoning_buffer:
                    self._print_file.write("\n\n")
                if self._print_chunk:
                    self._print_file.write(f"\033[7m{delta_data.reasoning_content}\033[0m")
                    self._print_file.flush()
                logger.trace("Received Reasoning_Content chunk: {reasoning_content}", user_id = self.user_id, reasoning_content = repr(delta_data.reasoning_content))
            self._content_buffer.reasoning_buffer.push_single_no_conversion(delta_data.reasoning_content)
        
        # 记录模型响应内容
        if delta_data.content:
            if self.request.print_chunk:
                if not self._content_buffer.content_buffer:
                    self._print_file.write("\n\n")
                if self._print_chunk:
                    self._print_file.write(delta_data.content)
                    self._print_file.flush()
                logger.trace("Received Content chunk: {content}", user_id = self.user_id, content = repr(delta_data.content))
            self._content_buffer.content_buffer.push_single_no_conversion(delta_data.content)
        
        # 记录模型工具调用内容
        if delta_data.tool_calls:
            for index, tool_call in enumerate(delta_data.tool_calls):
                if self.request.print_chunk:
                    if index not in self._content_buffer.tool_calls_arguments_buffer:
                        self._print_file.write("\n\n")
                        if tool_call.name:
                            self._print_file.write(f"\033[104m[Call Tool] {tool_call.name}:\n\033[0m")
                    elif self._print_chunk:
                        self._print_file.write(f"\033[104m{tool_call.arguments}\033[0m")
                        self._print_file.flush()
                    logger.trace(
                        "Received Tool_Call[{index}] chunk: {tool_call}",
                        user_id = self.user_id,
                        index = index,
                        tool_call = repr(tool_call)
                    )
                if index not in self.tool_calls:
                    self.tool_calls[index] = ToolCall()
                if tool_call.id:
                    self.tool_calls[index].id = tool_call.id
                if tool_call.type:
                    self.tool_calls[index].type = tool_call.type
                if tool_call.name:
                    self.tool_calls[index].name = tool_call.name
                if index not in self._content_buffer.tool_calls_arguments_buffer:
                    self._content_buffer.tool_calls_arguments_buffer[index] = TextBuffer()
                self._content_buffer.tool_calls_arguments_buffer[index].push_single_no_conversion(tool_call.arguments)
        
        if delta_data.system_fingerprint:
            self.response.system_fingerprint = delta_data.system_fingerprint

        # 判断是否为空并增加空chunk计数器
        if delta_data.is_empty:
            self.empty_chunk_count += 1
        self.chunk_count += 1

        if delta_data.finish_reason:
            self.response.finish_reason = delta_data.finish_reason
        
        # 刷新打印缓冲区
        if self.request.print_chunk:
            self._print_file.flush()
    @property
    def is_finished(self) -> bool:
        """
        Returns True if the streaming response generation layer has finished yielding data.
        """
        return self._finished