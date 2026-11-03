from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceDiskUsage(ToolPackage):
    class Params(BaseModel):
        path: str = Field(
            ...,
            description="The realspace path to measure (an empty string measures the root)."
        )

    name = "realspace_du"
    description = "Measure the total size and the file/directory counts below a realspace path."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_du")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.du(args.path)
