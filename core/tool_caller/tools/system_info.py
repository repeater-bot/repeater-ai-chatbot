import sys
from ..framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel
from ..._info import (
    __version__,
    __author__,
    __license__,
    __copyright__,
    __github__,
)

@ToolsCaller.register
class SystemInfo(ToolPackage):
    class Params(BaseModel):
        pass
    
    name = "system_info"
    description = "Get the system information."

    def base_info(self, runtime: RuntimePackage):
        global_configs = runtime.global_configs
        return {
            "name": global_configs.system_identification.system_name,
            "version": __version__,
            "author": __author__,
            "license": __license__,
            "copyright": __copyright__,
            "github": __github__,
            "system_identificationConfig": global_configs.system_identification.model_dump(),
            "runtime": sys.version,
        }

    async def call(self, args: Params, runtime: RuntimePackage):
        base_info = self.base_info(runtime)
        base_info.update(
            runtime.global_configs.tool_calls.tools_configs.system_info.extra_info
        )
        return base_info
