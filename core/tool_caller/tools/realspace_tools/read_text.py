from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field

@ToolsCaller.register
class RealspaceReadText(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The real text file path to read.")
        encoding: str = Field(default="utf-8", description="Text encoding used to decode the file.")

    name = "realspace_read_text"
    description = "Read a real text file with numbered lines, character offsets and metadata."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_read_text")
        return (await data_client.get_text_file(args.path, args.encoding)).model_dump()
