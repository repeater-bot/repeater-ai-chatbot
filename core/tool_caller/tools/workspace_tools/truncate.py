from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceTruncate(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to resize.")
        size: int = Field(..., ge=0, description="The target size in bytes.")

    name = "workspace_truncate"
    description = "Truncate or zero-extend a workspace file to an exact byte size."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.truncate(args.path, args.size)
