import asyncio

from loguru import logger
from pydantic import BaseModel, Field

from ..framework import ToolsCaller, ToolPackage, RuntimePackage

def _log_failure(task: asyncio.Task) -> None:
    """
    A background task that nobody awaits still has to report its failure.
    """
    if task.cancelled():
        return
    error = task.exception()
    if error is not None:
        logger.error("Bypass task failed: {error}", error = error)

@ToolsCaller.register
class Bypass(ToolPackage):
    """
    A task runs in the background, does not wait for it to finish, and gets its task id.
    """

    class Params(BaseModel):
        tool_name: str = Field(default=..., description="The name of the tool to run")
        args: str = Field(default=..., description="The arguments to pass to the tool. If not specified, lists tasks for all tools.")
        timeout: int | float | None = Field(default=None, description="The timeout in seconds for the tool to complete. If not specified, the tool will run indefinitely.")
        result_timeout: int | float | None = Field(default=None, description="The period of time after the end of the task during which you can use get to get the results, or permanently if you do not write.")

    name = "bypass"
    description = "A task runs in the background, does not wait for it to finish, and gets its task id."

    async def call(self, args: Params, runtime: RuntimePackage):
        running = await ToolsCaller.horizontal_create(
            tool = args.tool_name,
            args = args.args,
            runtime = runtime,
            timeout = args.timeout,
        )

        # The id goes back as a string: parse_result would not be able to
        # serialize a bare uuid.UUID.
        return str(running.task_id)
