from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel

@ToolsCaller.register
class GetHorizontalIds(ToolPackage):
    class Params(BaseModel):
        pass
    
    name = "get_horizontal_ids"
    description = "Gets a list of additional repeater instance ids that are horizontally accessible."

    async def call(self, args: Params, runtime: RuntimePackage):
        configs = runtime.global_configs.tool_calls.tools_configs.horizontal
        ids = list(configs.servers.keys())
        return ids
