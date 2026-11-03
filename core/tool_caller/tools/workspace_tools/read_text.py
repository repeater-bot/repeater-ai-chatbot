from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceReadText(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The text file path to read.")
        encoding: str = Field(default="utf-8", description="Text encoding used to decode the file.")

    name = "workspace_read_text"
    description = "Read a text file with numbered lines, character offsets and metadata."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        result = await data_client.get_text_file(args.path, args.encoding)
        return result.model_dump()
