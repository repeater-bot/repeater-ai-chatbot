from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceTouch(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to create or touch.")

    name = "workspace_touch"
    description = "Create an empty workspace file when missing, or refresh its timestamp."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.touch(args.path)
