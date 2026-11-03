from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field

@ToolsCaller.register
class RealspaceInfo(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The destination path to get metadata from.")

    name = "realspace_info"
    description = "Info about the realspace item."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_info")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.get_info(args.path)