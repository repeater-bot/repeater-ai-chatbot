import sys
from ...context import ToolCallPacakage
from .._caller import ModelRequester
from pydantic import BaseModel
from ..._info import (
    __version__,
    __author__,
    __license__,
    __copyright__,
    __github__,
)

@ModelRequester.reg_global_package
class SystemInfo(ToolCallPacakage):
    class Params(BaseModel):
        pass
    
    name = "system_info"
    description = "Get the system information."

    def base_info(self):
        return {
            "name": self.global_configs.system_identification.system_name,
            "version": __version__,
            "author": __author__,
            "license": __license__,
            "copyright": __copyright__,
            "github": __github__,
            "system_identificationConfig": self.global_configs.system_identification.model_dump(),
            "runtime": sys.version,
        }

    def call(self, args: Params):
        base_info = self.base_info()
        base_info.update(
            self.global_configs.tool_calls.tools_configs.system_info.extra_info
        )
        return base_info