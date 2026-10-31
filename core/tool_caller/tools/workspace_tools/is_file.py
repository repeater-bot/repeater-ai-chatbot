from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceIsFile(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The virtual path to check.")

    name = "workspace_is_file"
    description = "Check whether a virtual path is a file in the workspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.is_file(args.path)
