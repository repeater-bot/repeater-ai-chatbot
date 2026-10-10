import asyncio
import uuid

from typing import (
    Any,
    Generator,
    TextIO,
)
from types import FrameType
from dataclasses import dataclass

from .tool_package import ToolPackage
from .params_package import ParamsPackage


@dataclass(eq = False)
class RunningPackage:
    """
    运行中的命令包

    `eq` is disabled on purpose: equality and hashing are defined by hand below,
    because running packages are kept in sets and a dataclass generated
    `__eq__` would also drop the hand written `__hash__`.
    """
    task_id: uuid.UUID
    start_time: int
    start_monotonic_time: int
    timeout: int | float | None
    package: ToolPackage
    args: ParamsPackage
    task: asyncio.Task[int | None]

    def __hash__(self) -> int:
        return hash((type(self), self.task_id, self.task))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, RunningPackage):
            return self.task_id == __o.task_id and self.task == __o.task
        return False

    def get_coro(self):
        return self.task.get_coro()

    def get_name(self) -> str:
        return self.package.package_name

    def get_stack(self, *, limit: int | None = None) -> list[FrameType]:
        return self.task.get_stack(limit = limit)

    def print_stack(self, *, limit: int | None = None, file: TextIO | None = None) -> None:
        return self.task.print_stack(limit = limit, file = file)

    def __await__(self) -> Generator[Any, None, int | None]:
        return self.task.__await__()

    def cancel(self):
        self.task.cancel()
