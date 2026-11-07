from pydantic import BaseModel, Field
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client


@ToolsCaller.register
class RealspaceAppendText(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to append to.")
        text: str = Field(..., description="Text to append.")
        encoding: str = Field("utf-8", description="Encoding of the text.")

    name = "realspace_append_text"
    description = "Append text to a realspace file, creating it if missing."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_append_text")
        return await data_client.append_text(args.path, args.text, args.encoding)
