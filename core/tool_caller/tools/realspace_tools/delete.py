from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field

@ToolsCaller.register
class RealspaceDelete(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the file or directory to delete.")
        recursive: bool = Field(default=False, description="Whether to recursively delete the directory and its contents.")

    name = "realspace_delete"
    description = "Delete a file or directory from the realspace. Set recursive=true to delete a non-empty directory."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_delete")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.delete(
            args.path,
            recursive = args.recursive
        )