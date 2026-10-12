import uuid

from pydantic import BaseModel, Field

from ..framework import ToolsCaller, ToolPackage, RuntimePackage

@ToolsCaller.register
class ConsumptionOutput(ToolPackage):
    """
    Consumption output tool.
    """

    class Params(BaseModel):
        task_id: uuid.UUID = Field(default=..., description="The id of the tool to run")

    name = "consumption_output"
    description = "Wait to get the output of a command"

    async def call(self, args: Params, runtime: RuntimePackage):
        running = await ToolsCaller.get_running(args.task_id)
        if running is None:
            return f"No task with id {args.task_id}."

        output = await running.runtime.output.wait()
        return output
