import base64
from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field
from typing import Literal

@ToolsCaller.register
class RealspaceGetWhigteList(ToolPackage):
    class Params(BaseModel):
        pass

    name = "realspace_get_whitelist"
    description = "Get the whitelist of a file in the realspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_get_whitelist")
        global_runtime = RuntimeContainer.get_runtime()
        