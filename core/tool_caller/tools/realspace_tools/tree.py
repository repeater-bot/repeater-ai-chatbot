from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceTree(ToolPackage):
    class Params(BaseModel):
        path: str = Field(
            ...,
            description="The realspace path to walk (an empty string walks the root)."
        )
        max_depth: int = Field(
            default=-1,
            description="Maximum depth of the returned tree; -1 means unlimited."
        )

    name = "realspace_tree"
    description = "Return the nested node tree below a realspace path."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_tree")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.tree(
            args.path,
            max_depth = args.max_depth
        )
