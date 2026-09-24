from ...context import ToolCallPackage, CallMode
from ...data_manager import PromptManager
from .._caller import ModelRequester
from pydantic import BaseModel, Field

@ModelRequester.reg_global_package
class SetPrompt(ToolCallPackage):
    class Params(BaseModel):
        prompt: str = Field(..., description="The new prompt to set.")

    prompt_manager: PromptManager = PromptManager()
    name = "set_prompt"
    description = "Overrides the current system prompt."
    call_mode = CallMode.ASYNC

    async def call(self, args: Params):
        await self.prompt_manager.save(
            user_id = self.user_id,
            data = args.prompt
        )
        return "Prompt seted."