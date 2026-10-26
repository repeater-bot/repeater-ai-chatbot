from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceRematch(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The virtual path to match.")
        pattern: str = Field(
            ...,
            description="Python regular expression; re.match is used from the start of the path."
        )

    name = "workspace_rematch"
    description = "Check whether a virtual workspace path matches a regular expression."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.rematch(args.path, args.pattern)
