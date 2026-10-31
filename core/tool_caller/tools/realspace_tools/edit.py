import base64

from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceEdit(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to edit.")
        data: str = Field(..., description="Base64-encoded replacement bytes.")
        start: int = Field(..., ge=0, description="Start offset of the replaced range.")
        end: int = Field(..., ge=0, description="End offset (exclusive) of the replaced range.")

    name = "realspace_edit"
    description = "Replace a byte range in a realspace file with Base64-encoded bytes."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_edit")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.edit(
            args.path,
            base64.b64decode(args.data, validate = True),
            args.start,
            args.end
        )
