from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceMove(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The current path of the file or directory.")
        destination: str = Field(..., description="The new virtual path.")

    name = "workspace_move"
    description = "Move a file or directory in the workspace; file ids and payloads stay unchanged."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.move(args.path, args.destination)
