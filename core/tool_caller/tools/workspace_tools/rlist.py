from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceRlist(ToolPackage):
    class Params(BaseModel):
        path: str = Field(
            default="",
            description="The virtual directory to scan; an empty string means the workspace root."
        )

    name = "workspace_rlist"
    description = "Recursively list all descendant paths below a workspace directory."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.rlist(args.path)
