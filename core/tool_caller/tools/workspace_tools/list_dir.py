from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class WorkspaceList(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the directory to list (an empty string lists the root).")
        recursive: bool = Field(default=False, description="Whether to list all descendants recursively.")

    name = "workspace_list"
    description = "List direct child paths, or all descendants with recursive=true."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        result = await data_client.list_dir(
            args.path,
            recursive = args.recursive
        )
        return result