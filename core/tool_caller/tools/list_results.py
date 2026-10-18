from ..framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel

@ToolsCaller.register
class ListResult(ToolPackage):
    """
    List all completed tasks.
    """

    class Params(BaseModel):
        pass

    name = "list_results"
    description = "List all completed tasks ids."

    async def call(self, args: Params, runtime: RuntimePackage):
        runnings = await ToolsCaller.get_results(runtime.user_id, remove = False)
        text_buffer: list[str] = []
        if runnings:
            text_buffer.append("Completed tasks:")
            for running in runnings:
                text_buffer.append(f"{running.package.name} ({running.task_id})")
            return "\n".join(text_buffer)
        else:
            return "No completed tasks."
