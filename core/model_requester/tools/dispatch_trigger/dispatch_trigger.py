from ....context import ToolCallPacakage, CallMode
from ..._caller import ModelRequester
from pydantic import BaseModel, Field
from .request import DispatchTriggerRequest
from ....assist_struct import Response, RequestUserInfo
from .client import dispatch_trigger_client
from urllib.parse import urljoin

@ModelRequester.reg_global_package
class DispatchTrigger(ToolCallPacakage):
    class Params(BaseModel):
        bot_id: str = Field(default=..., description="The Bot id.")
        handler: str = Field(default=..., description="The target Handler that needs to be executed uses a Trigger match if it starts with a slash and a component ID match if it starts without a slash.")
        message: str = Field(default=..., description="The cq.code message that needs to be sent.")
        args: str | None = Field(default=None, description="Optionally, the message data will be overwritten when args is present.")
        message_id: int = Field(default=0, description="Message ID, which identifies the ID of the current message.")
        timeout: int = Field(default=2400, description="Timeout for the request.")
    
    name = "dispatch_trigger"
    description = "Make a request to the client based on the Repeater client communication protocol. (In some cases, the tool may not capture all of the returned content, depending on user feedback.)"
    call_mode = CallMode.ASYNC

    async def call(self, args: Params):
        configs = self.global_configs.tool_calls.tools_configs.dispatch_trigger
        base_url = configs.server_base_url

        if not base_url:
            raise ValueError("Invalid base URL")
        
        raw_response = await dispatch_trigger_client.post(
            url = urljoin(
                base = base_url,
                url = f"/repeater/api/external_trigger/call"
            ),
            json = DispatchTriggerRequest(
                bot_id = args.bot_id,
                handler = args.handler,
                namespace = self.user_id,
                message = args.message,
                args = args.args,
                message_id = args.message_id
            ).model_dump(exclude_none = True),
            timeout = args.timeout
        )

        return raw_response.text