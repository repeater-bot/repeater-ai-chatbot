import asyncio
from pydantic import BaseModel, Field

from ..framework import ToolsCaller, ToolPackage, RuntimePackage, ContentResult

@ToolsCaller.register
class Sleep(ToolPackage):
    """
    Sleep a specified amount of time.
    """

    class Params(BaseModel):
        sleep_time: int | float = Field(..., description="The amount of time to sleep.")

    name = "sleep"
    description = "Sleep a specified amount of time."

    async def call(self, args: Params, runtime: RuntimePackage):
        await asyncio.sleep(args.sleep_time)