from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceIsDir(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The virtual path to check.")

    name = "workspace_is_dir"
    description = "Check whether a virtual path is a directory in the workspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.is_dir(args.path)
