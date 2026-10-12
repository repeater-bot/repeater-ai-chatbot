import uuid

from typing import Any
from pydantic import BaseModel, Field

from ..framework import ToolsCaller, ToolPackage, RuntimePackage

@ToolsCaller.register
class ClearResult(ToolPackage):
    """
    Clear the result pool.
    """

    class Params(BaseModel):
        pass

    name = "clear_result"
    description = "Empty the result pool."

    async def call(self, args: Params, runtime: RuntimePackage):
        await ToolsCaller.reset_results(runtime.user_id)
        return "Results cleared."