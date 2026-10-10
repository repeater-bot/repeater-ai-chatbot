import orjson
import asyncio
from pydantic import BaseModel
from ...context import TextBlock, ContentBlock
from .content_result import ContentResult

class Output:
    def __init__(self):
        self.queue: asyncio.Queue[BaseModel | str | ContentResult] = asyncio.Queue()

    def __len__(self) -> int:
        return self.queue.qsize()

    async def put(self, item: BaseModel | str | ContentResult) -> None:
        await self.queue.put(item)

    def put_nowait(self, item: BaseModel | str | ContentResult) -> None:
        self.queue.put_nowait(item)
    
    def get_nowait(self) -> str | ContentResult | BaseModel | None:
        return self.queue.get_nowait()

    async def get(self) -> str | ContentResult | BaseModel:
        return await self.queue.get()

    async def get_all(self) -> list[str | ContentResult | BaseModel]:
        items: list[str | ContentResult | BaseModel] = []
        for _ in range(len(self)):
            items.append(await self.get())
        return items

    async def to_tool_response(self) -> str | list[ContentBlock]:

        # 该方法需要进行验证
        
        text_buffer: list[str] = []
        content_list: list[ContentBlock] = []
        for _ in range(len(self)):
            item = await self.get()
            if isinstance(item, str):
                text_buffer.append(item)
            elif isinstance(item, ContentResult):
                for block in item.content:
                    if isinstance(block, str):
                        text_buffer.append(block)
                    elif isinstance(block, TextBlock):
                        text_buffer.append(block.text)
                    else:
                        if text_buffer:
                            content_list.append(
                                TextBlock(
                                    text = "\n".join(text_buffer)
                                )
                            )
                        content_list.append(block)
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
