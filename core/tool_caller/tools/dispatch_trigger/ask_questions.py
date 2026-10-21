import random
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field
from .request import DispatchTriggerRequest
from .client import dispatch_trigger_client
from urllib.parse import urljoin

@ToolsCaller.register
class DispatchAskQuestions(ToolPackage):
    class Params(BaseModel):
        bot_id: str = Field(default=..., description="The Bot id.")
        ask_prompt: str = Field(default=..., description="The question to ask the user.")
        timeout: int = Field(default=2400, description="Timeout for the request.")
    
    name = "dispatch_trigger.ask_questions"
    description = (
        "Pose a question to the user and get the user's answer."
    )

    async def call(self, args: Params, runtime: RuntimePackage):
        configs = runtime.global_configs.tool_calls.tools_configs.dispatch_trigger
        base_url = configs.server_base_url

        if not base_url:
            raise ValueError("Invalid base URL")

        # Send Prompt
        if args.ask_prompt:
            raw_response = await dispatch_trigger_client.post(
                url = urljoin(
                    base = base_url,
                    url = "/repeater/api/external_trigger/call"
                ),
                json = DispatchTriggerRequest(
                    bot_id = args.bot_id,
                    handler = "/echo",
                    namespace = runtime.user_id,
                    message = args.ask_prompt,
                    args = None,
                    message_id = random.getrandbits(32),
                ).model_dump(exclude_none = True),
                timeout = args.timeout
            )

            if raw_response.status_code != 200:
                raise ValueError("Not sending prompt.")

        # Get Answer
        raw_response = await dispatch_trigger_client.post(
            url = urljoin(
                base = base_url,
                url = "/repeater/api/external_trigger/call"
            ),
            json = DispatchTriggerRequest(
                bot_id = args.bot_id,
                handler = "/npecho",
                namespace = runtime.user_id,
                message = "",
                args = None,
                message_id = random.getrandbits(32),
            ).model_dump(exclude_none = True),
            timeout = args.timeout
        )

        return raw_response.text
