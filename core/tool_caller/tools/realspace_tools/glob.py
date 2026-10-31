from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceGlob(ToolPackage):
    class Params(BaseModel):
        path: str = Field(
            default="",
            description="The virtual directory to scan; an empty string means the realspace root."
        )
        pattern: str = Field(
            ...,
            description="Glob pattern, for example '*.md', 'sub/*.md' or '**/*.md'."
        )
        recursive: bool = Field(
            default=False,
            description="Whether to match the pattern at any depth below the directory."
        )

    name = "realspace_glob"
    description = "List realspace paths matching a glob pattern below a directory."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_glob")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.glob(
            args.path,
            args.pattern,
            recursive = args.recursive
        )
