import aiofiles

from pydantic import BaseModel, Field
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from ._lock import file_lock

@ToolsCaller.register
class RealspaceAppendText(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to append to.")
        text: str = Field(..., description="Text to append.")
        encoding: str = Field("utf-8", description="Encoding of the text.")

    name = "realspace_append_text"
    description = "Appends text to file."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_append")
        async with file_lock:
            async with aiofiles.open(args.path, "a", encoding = args.encoding) as f:
                await f.write(args.text)