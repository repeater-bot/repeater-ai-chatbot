from ....framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field
from ..client import horizontal_client
from urllib.parse import urljoin
from ..gen_user_id import get_user_id

@ToolsCaller.register
class DeleteHorizontalContext(ToolPackage):
    class Params(BaseModel):
        instance_id: str = Field(default="", description="The instance ID to access.")
    
    name = "horizontal_access_delete_context"
    description = "Delete the chat context for specified instance with the local instance."

    async def call(self, args: Params, runtime: RuntimePackage):
        configs = runtime.global_configs.tool_calls.tools_configs.horizontal
        
        strategies = runtime.user_configs.horizontal_access_user_id_strategy
        if strategies is None:
            strategies = configs.user_id_strategy
        
        user_id = get_user_id(
            strategy = strategies,
            local_id = configs.local_id,
            user_id = runtime.user_id
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
