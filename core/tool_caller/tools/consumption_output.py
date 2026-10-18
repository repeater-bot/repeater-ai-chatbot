import uuid
import asyncio

from pydantic import BaseModel, Field
from ..framework import ToolsCaller, ToolPackage, RuntimePackage

@ToolsCaller.register
class ConsumptionOutput(ToolPackage):
    """
    Consumption output tool.
    """

    class Params(BaseModel):
        task_id: uuid.UUID = Field(default=..., description="The id of the tool to run")
        timeout: int | float | None = Field(default=None, description="The timeout of the tool")

    name = "consumption_output"
    description = "Wait to get the output of a command"

    async def call(self, args: Params, runtime: RuntimePackage):
        running = await ToolsCaller.get_running(args.task_id)
        if running is None:
            return f"No task with id {args.task_id}."

        if args.timeout is not None:
            output = await asyncio.wait_for(
                fut=asyncio.create_task(
                    coro=running.runtime.output.wait()
                ),
                timeout = args.timeout
            )
        else:
            output = await running.runtime.output.wait()
        return output
