from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceCopy(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The current path of the file or directory.")
        destination: str = Field(..., description="The new virtual path.")

    name = "realspace_copy"
    description = "Copy a file or directory in the realspace, allocating fresh file ids and payloads."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_copy")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.copy(args.path, args.destination)
