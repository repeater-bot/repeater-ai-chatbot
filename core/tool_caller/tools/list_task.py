from ..framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel

@ToolsCaller.register
class ListTask(ToolPackage):
    """
    Lists the tools that are currently running for the current user.
    """

    class Params(BaseModel):
        pass

    name = "list_task"
    description = "Lists the tools that are currently running for the current user."

    async def call(self, args: Params, runtime: RuntimePackage):
        runnings = await ToolsCaller.get_runnings(runtime.user_id)
        text_buffer: list[str] = []
        for running in runnings:
            text_buffer.append(f"{running.package.name} ({running.task_id})")

        if not text_buffer:
            return "No tool is running."
        return "\n".join(text_buffer)
