from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class WorkspaceDelete(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the file or empty directory to delete.")

    name = "workspace_delete"
    description = "Delete a file or an empty directory from the workspace. Non-empty directories are rejected."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.delete(args.path)