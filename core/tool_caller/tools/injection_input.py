import uuid
import asyncio

from typing import Any
from pydantic import BaseModel, Field

from ..framework import ToolsCaller, ToolPackage, RuntimePackage

@ToolsCaller.register
class InjectionInput(ToolPackage):
    """
    Injects input into a running tool
    """

    class Params(BaseModel):
        task_id: uuid.UUID = Field(default=..., description="The id of the tool to run")
        input: Any = Field(default=..., description="The input to inject")

    name = "injection_input"
    description = "Injects an input into the task."

    async def call(self, args: Params, runtime: RuntimePackage):
        running = await ToolsCaller.get_running(args.task_id)
        if running is None:
            return f"No task with id {args.task_id}."

        await running.runtime.input.put(args.input)
        return "Input injected."
