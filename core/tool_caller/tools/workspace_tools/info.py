from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class WorkspaceInfo(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The destination path to get metadata from.")

    name = "workspace_info"
    description = "Info about the workspace item."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.get_info(args.path)