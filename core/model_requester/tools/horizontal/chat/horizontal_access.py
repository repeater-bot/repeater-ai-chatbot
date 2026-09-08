from .....context import ToolCallPacakage, CallMode
from ...._caller import ModelRequester
from pydantic import BaseModel, Field
from .request_body import ChatRequest
from .....assist_struct import Response, RequestUserInfo
from ..client import horizontal_client
from urllib.parse import urljoin

@ModelRequester.reg_global_package
class HorizontalAccess(ToolCallPacakage):
    class Params(BaseModel):
        instance_id: str = Field(default="", description="The instance ID to access.")
        message: str = Field(default="", description="The message to send to the instance.")
        thinking: bool | None = Field(default=None, description="Whether to show thinking indicator.")
        timeout: int | float | None = Field(default=600, description="The timeout for the request.")
    
    name = "horizontal_access"
    description = "Chats to the specified Repeater instance."
    call_mode = CallMode.ASYNC
    json_result = True

    async def call(self, args: Params):
        configs = self.global_configs.tool_calls.tools_configs.horizontal
        user_id = configs.user_id
        if configs.with_now_user_id:
            user_id = f"{user_id}_{self.user_id}"
        url = configs.servers.get(args.instance_id)
        if not url:
            raise ValueError("Invalid instance ID")
        
        raw_response = await horizontal_client.post(
            url = urljoin(
                base = url,
                url = f"/generate/chat/completion/{user_id}"
            ),
            json = ChatRequest(
                message = args.message,
                thinking = args.thinking,
                user_info = RequestUserInfo(
                    **configs.user_info.model_dump(exclude_none = True)
                )
            ).model_dump(exclude_none = True),
            timeout = args.timeout
        )

        response = Response(**raw_response.json())
        if response.context:
            return response.context.model_dump(exclude_none = True)
        else:
            raise ValueError("Invalid response")