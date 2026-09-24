from ....context import ToolCallPackage
from ..._caller import ModelRequester
from pydantic import BaseModel

@ModelRequester.reg_global_package
class GetHorizontalIds(ToolCallPackage):
    class Params(BaseModel):
        pass
    
    name = "get_horizontal_ids"
    description = "Gets a list of additional repeater instance ids that are horizontally accessible."
    json_result = True

    def call(self, args: Params):
        configs = self.global_configs.tool_calls.tools_configs.horizontal
        ids = list(configs.servers.keys())
        return ids