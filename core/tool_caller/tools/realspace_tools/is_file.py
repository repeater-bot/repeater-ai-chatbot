from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceIsFile(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The virtual path to check.")

    name = "realspace_is_file"
    description = "Check whether a virtual path is a file in the realspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_is_file")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.is_file(args.path)
