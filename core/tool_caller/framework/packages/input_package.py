import asyncio
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar("T")

@dataclass
class IOStreamPackage(Generic[T]):
    """
    Class that represents the input package for the tool.
    """
    queue: asyncio.Queue[T]

    async def wait(self) -> T:
        """
        Get the next item from the queue.
        """
        return await self.queue.get()

    async def put(self, item: T) -> None:
        """
        Put an item into the queue.
        """
        await self.queue.put(item)

    def __len__(self) -> int:
        """
        Return the number of items in the queue.
        """
        return self.queue.qsize()

    def __bool__(self) -> bool:
        """
        Return True if the queue is not empty.
        """
        return not self.queue.empty()