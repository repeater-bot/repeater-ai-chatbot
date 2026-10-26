from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceGlob(ToolPackage):
    class Params(BaseModel):
        path: str = Field(
            default="",
            description="The virtual directory to scan; an empty string means the workspace root."
        )
        pattern: str = Field(
            ...,
            description="Glob pattern, for example '*.md', 'sub/*.md' or '**/*.md'."
        )

    name = "workspace_glob"
    description = "List workspace paths matching a glob pattern below a directory."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.glob(args.path, args.pattern)
