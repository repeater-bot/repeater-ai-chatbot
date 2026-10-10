import asyncio
from typing import Any

import orjson
from pydantic import BaseModel

from ...context import (
    ContentBlock,
    ContentResult,
    TextBlock,
    is_content_block,
)

ContentItem = str | ContentResult | BaseModel | list[Any]
"""Anything a tool may push into its output. Every content block is a BaseModel."""


class Output:
    """
    The output channel of a single tool call.

    A tool pushes whatever it wants the model to see into this queue; the
    framework merges the queued items into one tool response through
    `to_tool_response`. Text and text blocks are joined into a single text
    segment, every other content block is kept in place, so the relative order
    of the pushed items is preserved.
    """

    def __init__(self):
        self.queue: asyncio.Queue[ContentItem] = asyncio.Queue()

    def __len__(self) -> int:
        return self.queue.qsize()

    def __bool__(self) -> bool:
        return not self.queue.empty()

    async def put(self, item: ContentItem) -> None:
        """
        Push an item into the output.

        :param item: The item to push.
        """
        await self.queue.put(item)

    def put_nowait(self, item: ContentItem) -> None:
        """
        Push an item into the output without awaiting.

        :param item: The item to push.
        """
        self.queue.put_nowait(item)

    def get_nowait(self) -> ContentItem:
        """
        Pop the oldest item of the output.

        :return: The oldest item.
        :raises asyncio.QueueEmpty: If the output is empty.
        """
        return self.queue.get_nowait()

    async def get(self) -> ContentItem:
        """
        Pop the oldest item of the output, waiting for one if it is empty.

        :return: The oldest item.
        """
        return await self.queue.get()

    def drain(self) -> list[ContentItem]:
        """
        Pop every item that is currently queued.

        :return: The items, oldest first.
        """
        items: list[ContentItem] = []
        while not self.queue.empty():
            try:
                items.append(self.queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return items

    async def get_all(self) -> list[ContentItem]:
        """
        Pop every item that is currently queued.

        :return: The items, oldest first.
        """
        return self.drain()

    async def to_tool_response(self) -> str | list[ContentBlock]:
        """
        Merge everything that is queued into a single tool response.

        This drains the output.

        :return: The merged tool response.
        """
        text_buffer: list[str] = []
        content_list: list[ContentBlock] = []

        def flush_text() -> None:
            if text_buffer:
                content_list.append(
                    TextBlock(
                        text = "\n".join(text_buffer)
                    )
                )
                text_buffer.clear()

        def add_block(block: ContentBlock | str | BaseModel) -> None:
            if isinstance(block, str):
                text_buffer.append(block)
            elif isinstance(block, TextBlock):
                text_buffer.append(block.text)
            elif is_content_block(block):
                flush_text()
                content_list.append(block)
            else:
                text_buffer.append(str(block))

        def add_item(item: ContentItem) -> None:
            if isinstance(item, str):
                text_buffer.append(item)
            elif isinstance(item, ContentResult):
                content = item.content
                if isinstance(content, str):
                    text_buffer.append(content)
                else:
                    for block in content:
                        add_block(block)
            elif isinstance(item, BaseModel):
                text_buffer.append(
                    orjson.dumps(item.model_dump()).decode("utf-8")
                )
            elif isinstance(item, (list, tuple)):
                for block in item:
                    add_block(block)
            else:
                add_block(item)

        for item in self.drain():
            add_item(item)

        if content_list:
            flush_text()
            return content_list

        return "\n".join(text_buffer)
