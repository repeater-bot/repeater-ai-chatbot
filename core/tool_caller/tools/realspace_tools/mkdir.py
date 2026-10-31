from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceMkdir(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The directory path to create, including missing parents.")

    name = "realspace_mkdir"
    description = "Create an empty directory in the realspace, including missing parents."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_mkdir")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.mkdir(args.path)
