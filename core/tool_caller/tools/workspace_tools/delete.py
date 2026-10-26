from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class WorkspaceDelete(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the file or directory to delete.")
        recursive: bool = Field(default=False, description="Whether to recursively delete the directory and its contents.")

    name = "workspace_delete"
    description = "Delete a file or directory from the workspace. Set recursive=true to delete a non-empty directory."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.delete(
            args.path,
            recursive = args.recursive
        )