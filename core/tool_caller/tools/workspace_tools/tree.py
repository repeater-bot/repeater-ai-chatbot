from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceTree(ToolPackage):
    class Params(BaseModel):
        path: str = Field(
            ...,
            description="The workspace path to walk (an empty string walks the root)."
        )
        max_depth: int = Field(
            default=-1,
            description="Maximum depth of the returned tree; -1 means unlimited."
        )

    name = "workspace_tree"
    description = "Return the nested node tree below a workspace path."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.tree(
            args.path,
            max_depth = args.max_depth
        )
