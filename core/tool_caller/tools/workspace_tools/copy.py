from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceCopy(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The current path of the file or directory.")
        destination: str = Field(..., description="The new virtual path.")

    name = "workspace_copy"
    description = "Copy a file or directory in the workspace, allocating fresh file ids and payloads."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.copy(args.path, args.destination)
