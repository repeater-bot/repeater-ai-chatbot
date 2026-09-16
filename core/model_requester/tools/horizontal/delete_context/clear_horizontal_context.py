from .....context import ToolCallPacakage, CallMode
from ...._caller import ModelRequester
from pydantic import BaseModel, Field
from ..client import horizontal_client
from urllib.parse import urljoin
from ..gen_user_id import get_user_id

@ModelRequester.reg_global_package
class DeleteHorizontalContext(ToolCallPacakage):
    class Params(BaseModel):
        instance_id: str = Field(default="", description="The instance ID to access.")
    
    name = "delete_horizontal_context"
    description = "Delete the chat context for specified instance with the local instance."
    call_mode = CallMode.ASYNC
    json_result = True

    async def call(self, args: Params):
        configs = self.global_configs.tool_calls.tools_configs.horizontal
        
        strategies = self.user_configs.horizontal_access_user_id_strategy
        if strategies is None:
            strategies = configs.user_id_strategy
        
        user_id = get_user_id(
            strategy = strategies,
            local_id = configs.local_id,
            user_id = self.user_id
        )
        url = configs.servers.get(args.instance_id)
        if not url:
            raise ValueError("Invalid instance ID")
        
        response = await horizontal_client.delete(
            url = urljoin(
                base = url,
                url = f"/userdata/context/delete/{user_id}",
            )
        )
        return response.text