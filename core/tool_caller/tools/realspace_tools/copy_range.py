from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceCopyRange(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The source file path to copy a range from.")
        destination: str = Field(..., description="The destination path of the copied range.")
        start: int = Field(..., ge=0, description="Start offset of the copied range.")
        end: int = Field(..., ge=0, description="End offset (exclusive) of the copied range.")

    name = "realspace_copy_range"
    description = "Copy a byte range of a realspace file into a new file."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_copy_range")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.copy_range(
            args.path,
            args.destination,
            args.start,
            args.end
        )
