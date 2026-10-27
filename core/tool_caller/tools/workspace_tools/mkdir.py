from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceMkdir(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The directory path to create, including missing parents.")

    name = "workspace_mkdir"
    description = "Create an empty directory in the workspace, including missing parents."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.mkdir(args.path)
