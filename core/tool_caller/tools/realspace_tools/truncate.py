from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceTruncate(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to resize.")
        size: int = Field(..., ge=0, description="The target size in bytes.")

    name = "realspace_truncate"
    description = "Truncate or zero-extend a realspace file to an exact byte size."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_truncate")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.truncate(args.path, args.size)
