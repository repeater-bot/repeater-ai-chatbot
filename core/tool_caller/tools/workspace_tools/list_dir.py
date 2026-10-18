from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class WorkspaceList(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the directory to list (an empty string lists the root).")

    name = "workspace_list"
    description = "List all items in a directory in the workspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        result = await data_client.list_dir(args.path)
        return result