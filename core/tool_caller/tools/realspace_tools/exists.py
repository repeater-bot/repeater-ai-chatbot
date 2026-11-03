from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceExists(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The virtual path to check.")

    name = "realspace_exists"
    description = "Check whether a virtual path exists in the realspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_exists")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.exists(args.path)
