import base64

from pydantic import BaseModel, Field
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client


@ToolsCaller.register
class RealspaceAppend(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to append to.")
        data: str = Field(..., description="Base64-encoded bytes to append.")

    name = "realspace_append"
    description = "Append Base64-encoded bytes to a realspace file, creating it if missing."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_append")
        return await data_client.append(
            args.path,
            base64.b64decode(args.data, validate = True)
        )
