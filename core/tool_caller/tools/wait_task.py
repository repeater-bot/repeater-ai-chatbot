import uuid

from pydantic import BaseModel

from ..framework import ToolsCaller, ToolPackage, RuntimePackage, ContentResult

@ToolsCaller.register
class WaitTask(ToolPackage):
    """
    Waits for a task that was started by `bypass` and returns its result.
    """

    class Params(BaseModel):
        task_id: uuid.UUID

    name = "wait_task"
    description = "Waits for a task that was started by bypass and returns its result."

    async def call(self, args: Params, runtime: RuntimePackage):
        running = await ToolsCaller.get_running(args.task_id)
        if running is None:
            return f"No task with id {args.task_id}."

        result = await running
        return ContentResult(
            content = result.content
        )
