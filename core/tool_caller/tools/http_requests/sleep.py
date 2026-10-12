import asyncio
from typing import Literal
from pydantic import BaseModel, Field

class Sleep(BaseModel):
    type: Literal["sleep"] = "sleep"
    sleep_seconds: int | float = Field(..., description="The number of seconds to sleep.")

    async def sleep(self):
        await asyncio.sleep(self.sleep_seconds)
