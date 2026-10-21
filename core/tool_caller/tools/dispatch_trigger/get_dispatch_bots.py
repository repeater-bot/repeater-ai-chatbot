from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field
from .client import dispatch_trigger_client
from urllib.parse import urljoin

@ToolsCaller.register
class GetDispatchBots(ToolPackage):
    class Params(BaseModel):
        timeout: int = Field(60, description="Request timeout")
    
    name = "dispatch_trigger.get_bots"
    description = "Get the list of Bots supported in the client based on the Repeater client communication protocol."

    async def call(self, args: Params, runtime: RuntimePackage):
        configs = runtime.global_configs.tool_calls.tools_configs.dispatch_trigger
        base_url = configs.server_base_url

        if not base_url:
            raise ValueError("Invalid base URL")
        
        raw_response = await dispatch_trigger_client.get(
            url = urljoin(
                base = base_url,
                url = f"/repeater/api/external_trigger/bots_list"
            ),
            timeout = args.timeout
        )

        return raw_response.text
