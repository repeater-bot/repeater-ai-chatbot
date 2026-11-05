import base64
import aiofiles

from pydantic import BaseModel, Field
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from ._lock import file_lock

@ToolsCaller.register
class RealspaceAppend(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to append to.")
        data: str = Field(..., description="Base64-encoded bytes to append.")

    name = "realspace_append"
    description = "Appends base64 encoded bytes to file."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_append")
        async with file_lock:
            async with aiofiles.open(args.path, "ab") as f:
                await f.write(
                    base64.b64decode(
                        args.data
                    )
                )