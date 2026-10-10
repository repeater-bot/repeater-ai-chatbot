from ...data_manager import PromptManager
from ..framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class SetPrompt(ToolPackage):
    class Params(BaseModel):
        prompt: str = Field(..., description="The new prompt to set.")

    prompt_manager: PromptManager = PromptManager()
    name = "set_prompt"
    description = "Overrides the current system prompt."

    async def call(self, args: Params, runtime: RuntimePackage):
        await self.prompt_manager.save(
            user_id = runtime.user_id,
            data = args.prompt
        )
        return "Prompt seted."
