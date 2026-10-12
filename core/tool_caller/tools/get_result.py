import uuid

from typing import Any
from pydantic import BaseModel, Field

from ..framework import ToolsCaller, ToolPackage, RuntimePackage

@ToolsCaller.register
class GetResult(ToolPackage):
    """
    Get the result of a tool
    """

    class Params(BaseModel):
        task_id: uuid.UUID = Field(default=..., description="The id of the tool to run")
        input: Any = Field(default=..., description="The input to inject")

    name = "get_result"
    description = "When the task finishes, get its results and remove them from the result pool."

    async def call(self, args: Params, runtime: RuntimePackage):
        running = await ToolsCaller.get_result(args.task_id, runtime.user_id)
        if running is None:
            return f"No result with id {args.task_id}."

        if running.done():
            return running.result()
        else:
            return f"Result with id {running.task_id} is still running."