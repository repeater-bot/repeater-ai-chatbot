from __future__ import annotations

import orjson

from pydantic import BaseModel
from abc import ABC, abstractmethod
from .runtime_package import RuntimePackage
from typing import Any
from ....context import (
    ContentUnit,
    ContentRole,
    ContentBlock,
    TextBlock,
    ToolTypes,
    is_content_block
)
from ..content_result import ContentResult
from ..make_content_result import create_tool_content_unit
from ..tool_request import ToolStruct, FunctionStruct

class ToolPackage(ABC):

    name: str
    """The name of the tool"""
    description: str
    """The description of the tool"""
    force_choice: bool = False
    """Whether the tool should be forced to be chosen by the user"""

    class Params(BaseModel):
        pass

    class Result(BaseModel):
        pass

    @abstractmethod
    async def call(self, args: BaseModel, runtime: RuntimePackage) -> Any:
        pass

    async def enter_tool(self, args: BaseModel, runtime: RuntimePackage) -> Any:
        return await self.call(args, runtime)

    def parse_params(self, args: str) -> Params:
        data = orjson.loads(args)
        return self.Params(**data)
    
    def on_error(self, error: BaseException) -> Any:
        return f"Tool {self.name} error: {error}"

    def parse_result(
            self,
            result: Any,
            tool_call_id: str,
            loop_times: int | None = None,
            max_loop_times: int | None = None
        ) -> ContentUnit:
        text_buffer: list[str] = []
        block_buffer: list[ContentBlock] = []

        if isinstance(result, str):
            text_buffer.append(result)
        elif isinstance(result, ContentResult):
            if isinstance(result.content, str):
                text_buffer.append(result.content)
            else:
                for block in result.content:
                    if isinstance(block, TextBlock):
                        text_buffer.append(block.text)
                    elif is_content_block(block):
                        if text_buffer:
                            block_buffer.append(
                                TextBlock(
                                    text = "\n".join(text_buffer)
                                )
                            )
                            text_buffer = []
                        block_buffer.append(block)
                    else:
                        raise ValueError(f"Invalid block type: {type(block).__name__}")
        elif isinstance(result, BaseModel):
            # A tool may return one of its `Result` models; orjson can not
            # serialize a pydantic model directly, so dump it first.
            try:
                text_buffer.append(orjson.dumps(result.model_dump()).decode("utf-8"))
            except Exception as e:
                text_buffer.append(f"Result Encode Error: {e}")
        else:
            try:
                text_buffer.append(orjson.dumps(result).decode("utf-8"))
            except Exception as e:
                text_buffer.append(str(e))

        if block_buffer:
            if text_buffer:
                block_buffer.append(
                    TextBlock(
                        text = "\n".join(text_buffer)
                    )
                )
            return create_tool_content_unit(
                tool_call_id = tool_call_id,
                content = block_buffer,
                loop_times = loop_times,
                max_loop_times = max_loop_times
            )
        else:
            return create_tool_content_unit(
                tool_call_id = tool_call_id,
                content = "\n".join(text_buffer),
                loop_times = loop_times,
                max_loop_times = max_loop_times
            )
    
    def to_request(self, strict: bool = True) -> ToolStruct:
        return ToolStruct(
            type = ToolTypes.FUNCTION,
            function = FunctionStruct(
                name = self.name,
                description = self.description,
                parameters = self.Params.model_json_schema(),
                strict = strict,
            )
        )