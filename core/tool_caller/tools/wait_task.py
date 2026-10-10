import uuid
from ..framework import ToolsCaller, ToolPackage
from pydantic import BaseModel

@ToolsCaller.register
class ListTask(ToolPackage):
    """
    Lists the tools that are currently running for the current user.
    """

    class Params(BaseModel):
        task_id: uuid.UUID

    name = "wait_task"
    description = "Lists the tools that are currently running for the current user."

    async def call(self, args: Params):
        running = await ToolsCaller.get_running(self.user_id, args.task_id)
        if running is None:
            return None
        else:
            result = await running
            running.args.output
