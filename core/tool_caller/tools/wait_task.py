import uuid
import asyncio
from pydantic import BaseModel, Field

from ..framework import ToolsCaller, ToolPackage, RuntimePackage, ContentResult

@ToolsCaller.register
class WaitTask(ToolPackage):
    """
    Waits for a task that was started by `bypass` and returns its result.
    """

    class Params(BaseModel):
        task_id: uuid.UUID = Field(..., description="The ID of the task to wait for.")
        timeout: int | float | None = Field(None, description="The maximum time to wait for the task to complete.")
        timeout_cancellation: bool = Field(False, description="Whether to cancel the task if it takes too long to complete.")

    name = "wait_task"
    description = "Waits for a task that was started by bypass and returns its result."

    async def call(self, args: Params, runtime: RuntimePackage):
        running = await ToolsCaller.get_running(args.task_id)
        if running is None:
            return f"No task with id {args.task_id}."

        if args.timeout_cancellation:
            try:
                result = await asyncio.wait_for(
                    running.task,
                    timeout = args.timeout
                )
                if not running.task.done():
                    running.task.cancel()
            except (asyncio.TimeoutError, asyncio.CancelledError):
                return f"Task {running.task_id} timeout."
        else:
            shield_task = asyncio.shield(running.task)

            try:
                result = await asyncio.wait_for(
                    shield_task,
                    timeout = args.timeout
                )
            except asyncio.TimeoutError:
                return f"Task {running.task_id} timeout."
        return ContentResult(
            content = result.content
        )