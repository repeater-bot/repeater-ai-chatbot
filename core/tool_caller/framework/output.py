import orjson
import asyncio
from pydantic import BaseModel
from ...context import ContentBlock, TextBlock, is_content_block

class Output:
    def __init__(self):
        self.queue: asyncio.Queue[BaseModel | str | ContentBlock] = asyncio.Queue()

    def __len__(self) -> int:
        return self.queue.qsize()

    async def put(self, item: BaseModel | str | ContentBlock) -> None:
        await self.queue.put(item)

    def put_nowait(self, item: BaseModel | str | ContentBlock) -> None:
        self.queue.put_nowait(item)
    
    def get_nowait(self) -> str | ContentBlock | BaseModel | None:
        return self.queue.get_nowait()

    async def get(self) -> str | ContentBlock | BaseModel:
        return await self.queue.get()

    async def get_all(self) -> list[str | ContentBlock | BaseModel]:
        items: list[str | ContentBlock | BaseModel] = []
        for _ in range(len(self)):
            items.append(await self.get())
        return items

    async def to_tool_response(self) -> str | list[ContentBlock]:
        text_buffer: list[str] = []
        content_list: list[ContentBlock] = []
        for _ in range(len(self)):
            item = await self.get()
            if isinstance(item, str):
                text_buffer.append(item)
            elif isinstance(item, TextBlock):
                text_buffer.append(item.text)
            elif is_content_block(item):
                if text_buffer:
                    content_list.append(
                        TextBlock(
                            text = "\n".join(text_buffer)
                        )
                    )
                content_list.append(item)
                text_buffer = []
            elif isinstance(item, BaseModel):
                text_buffer.append(orjson.dumps(item.model_dump()).decode())

        if content_list:
            if text_buffer:
                content_list.append(
                    TextBlock(
                        text = "\n".join(text_buffer)
                    )
                )
            return content_list
        else:
            return "\n".join(text_buffer)
