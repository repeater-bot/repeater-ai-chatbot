from ....global_config_manager import ConfigManager
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel


@ToolsCaller.register
class RealspaceGetWhitelist(ToolPackage):
    class Params(BaseModel):
        pass

    name = "realspace_get_whitelist"
    description = "Return the configured realspace whitelist entries and their allowed operations."

    async def call(self, args: Params, runtime: RuntimePackage):
        units = ConfigManager.get_configs().tool_calls.tools_configs.realspace.whitelist
        return {
            key: unit.model_dump(by_alias = True)
            for key, unit in units.items()
        }
