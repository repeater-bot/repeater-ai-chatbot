from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceCopyRange(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The source file path to copy a range from.")
        destination: str = Field(..., description="The destination path of the copied range.")
        start: int = Field(..., ge=0, description="Start offset of the copied range.")
        end: int = Field(..., ge=0, description="End offset (exclusive) of the copied range.")

    name = "workspace_copy_range"
    description = "Copy a byte range of a workspace file into a new file."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.copy_range(
            args.path,
            args.destination,
            args.start,
            args.end
        )
