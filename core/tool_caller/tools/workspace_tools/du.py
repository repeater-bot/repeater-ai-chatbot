from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceDiskUsage(ToolPackage):
    class Params(BaseModel):
        path: str = Field(
            ...,
            description="The workspace path to measure (an empty string measures the root)."
        )

    name = "workspace_du"
    description = "Measure the total size and the file/directory counts below a workspace path."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.du(args.path)
