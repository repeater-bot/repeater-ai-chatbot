from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field

@ToolsCaller.register
class RealspaceList(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the directory to list (an empty string lists the root).")
        recursive: bool = Field(default=False, description="Whether to list all descendants recursively.")

    name = "realspace_list"
    description = "List direct child paths, or all descendants with recursive=true."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_list")
        global_runtime = RuntimeContainer.get_runtime()

        result = await data_client.list_dir(
            args.path,
            recursive = args.recursive
        )
        return result