import uuid
from ..framework import ToolsCaller, ToolPackage, ParamsPackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class Bypass(ToolPackage):
    """
    A task runs in the background, does not wait for it to finish, and gets its task id.
    """

    class Params(BaseModel):
        tool_name: str = Field(default=..., description="The name of the tool to run")
        args: str = Field(default=..., description="The arguments to pass to the tool. If not specified, lists tasks for all tools.")
        timeout: int | float | None = Field(default=None, description="The timeout in seconds for the tool to complete. If not specified, the tool will run indefinitely.")

    name = "bypass"
    description = "A task runs in the background, does not wait for it to finish, and gets its task id."

    async def call(self, args: Params):
        package = ToolsCaller.match_tool(args.tool_name)
        running = await ToolsCaller.horizontal_enter_wait_created(
            user_id = self.user_id,
            package = package,
            args = ToolsCaller.call_tools(
                user_id = self.user_id,
                
            ),
            timeout = timeout
        )
        return running.task_id