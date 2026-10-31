from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceIsDir(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The virtual path to check.")

    name = "realspace_is_dir"
    description = "Check whether a virtual path is a directory in the realspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_is_dir")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.is_dir(args.path)
