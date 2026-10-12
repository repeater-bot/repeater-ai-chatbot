from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from ....auxiliary.text import text_content_cutter
from .._exceptions import *
from ._content_role import ContentRole
from ._content_block import (
    ContentBlock,
    TextBlock,
    ImageBlock,
    VideoBlock,
    AudioBlock,
    FileBlock
)
from ._function_calling_response import CallingRequest
from ....text_buffer import TextBuffer, IndentedText
from typing import Any, Type

class ContentUnit(BaseModel):
    """
    上下文单元
    """
    model_config = ConfigDict(
        validate_assignment = True
    )

    reasoning_content: str | None = None
    content: str | list[ContentBlock] = ""
    role: ContentRole = ContentRole.USER
    role_name: str |  None = None
    prefix: bool | None = None
    created: datetime = Field(default_factory=datetime.now)
    tool_calls: list[CallingRequest] | None = None
    tool_call_id: str | None = None

    def __len__(self) -> int:
        length: int = 0
        if isinstance(self.content, str):
            length = len(self.content)
        else:
            for block in self.content:
                if isinstance(block, TextBlock):
                    length += len(block.text)
        if self.reasoning_content:
            length += len(self.reasoning_content)
        return length
    
    def only_context_block(self, block_type: Type[ContentBlock]) -> bool:
        """
        检查上下文单元是否只包含指定类型的ContentBlock
        """
        if isinstance(self.content, str):
            raise ContentUnitError("ContentUnit is not a list of ContentBlock")
        for block in self.content:
            if not isinstance(block, block_type):
                return False
        return True
    
    def remove_context_block(self, *block_type: Type[ContentBlock]) -> ContentUnit:
        """
        移除指定类型的上下文块
        """
        if isinstance(self.content, str):
            raise ContentUnitError("ContentUnit is not a list of ContentBlock")
        new_content: list[ContentBlock] = []
        for block in self.content:
            if not isinstance(block, block_type):
                new_content.append(block)
        new = self.model_copy()
        new.content = new_content
        return new
    
    def to_plaintext_content(self) -> str:
        if isinstance(self.content, str):
            return self.content
        else:
            text_buffer: TextBuffer = TextBuffer()
            for block in self.content:
                if isinstance(block, TextBlock):
                    text_buffer.push(block.text)
            return str(text_buffer)
 
    def to_content(
            self,
            remove_reasoning_prompt: bool = False,
            remove_created: bool = False
        ) -> dict[str, Any]:
        exclude: set[str] = set()
        
        if remove_reasoning_prompt:
            exclude.add("reasoning_content")
        if remove_created:
            exclude.add("created")
        
        if exclude:
            return self.model_dump(exclude = exclude)
        return self.model_dump()
    
    def to_text(
            self,
            remove_reasoning_prompt: bool = False,
        ) -> str:
        buffer: list[str] = []
        if not remove_reasoning_prompt and self.reasoning_content:
            buffer.append(self.reasoning_content)
        
        if self.content:
            if isinstance(self.content, str):
                buffer.append(self.content)
            elif isinstance(self.content, list):
                for block in self.content:
                    if isinstance(block, TextBlock):
                        buffer.append(block.text)
            else:
                raise TypeError(f"Unsupported content type: {type(self.content).__name__}")
        
        return "\n".join(buffer)
    
    def __bool__(self) -> bool:
        return bool(self.content) or bool(self.reasoning_content) or bool(self.tool_call_id)
    
    def reduce_to_text(self) -> ContentUnit:
        if isinstance(self.content, list):
            buffer: TextBuffer = TextBuffer(separator="\n")
            for block in self.content:
                if isinstance(block, TextBlock):
                    buffer.push(block.text)
            new = self.model_copy()
            new.content = str(buffer)
            return new
        else:
            return self
    
    def content_to_string(self, non_text_length_limit: int | None = 10) -> str:
        if isinstance(self.content, str):
            return self.content
        else:
            message_texts: TextBuffer = TextBuffer()
            for block in self.content:
                if isinstance(block, TextBlock):
                    message_texts.push(block.text)
                elif isinstance(block, ImageBlock):
                    message_texts.push(
                        f"[Image: {text_content_cutter(block.image_url.url, non_text_length_limit)}]"
                    )
                elif isinstance(block, VideoBlock):
                    message_texts.push(
                        f"[Video: {text_content_cutter(block.video_url.url, non_text_length_limit)}]"
                    )
                elif isinstance(block, AudioBlock):
                    message_texts.push(
                        f"[Audio: {text_content_cutter(block.input_audio.data, non_text_length_limit)}]"
                    )
                elif isinstance(block, FileBlock):
                    message_texts.push(
                        f"[File: {text_content_cutter(block.file.filename, non_text_length_limit)}]"
                    )
                else:
                    message_texts.push(f"[Unknown Block: {block}]")
        
            return "\n".join(message_texts)

    def __str__(self) -> str:
        text_buffer: TextBuffer = TextBuffer()
        if self.reasoning_content:
            text_buffer.push("Reasoning:")
            text_buffer.push(
                IndentedText(
                    self.reasoning_content,
                    indent_level = 2,
                )
            )
        if self.content:
            text_buffer.push("Content:")
            text_buffer.push(
                IndentedText(
                    self.content_to_string(),
                    indent_level = 2,
                )
            )
        return str(text_buffer)