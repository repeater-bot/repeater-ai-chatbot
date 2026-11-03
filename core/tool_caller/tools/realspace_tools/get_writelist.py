from ....global_config_manager import ConfigManager
from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel


@ToolsCaller.register
class RealspaceGetWritelist(ToolPackage):
    class Params(BaseModel):
        pass

    name = "realspace_get_writelist"
    description = "Return the configured realspace whitelist entries and their allowed operations."

    async def call(self, args: Params, runtime: RuntimePackage):
        units = ConfigManager.get_configs().tool_calls.tools_configs.realspace.writelist
        return [
            unit.model_dump(by_alias = True)
            for unit in units
        ]
