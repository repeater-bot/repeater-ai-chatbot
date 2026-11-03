import base64
from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field
from typing import Literal

@ToolsCaller.register
class RealspaceGetUrl(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the file to read.")

    name = "realspace_get_url"
    description = "Get the URL of a file in the realspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_get_url")
        global_runtime = RuntimeContainer.get_runtime()

        url = await data_client.get_file_url(
            args.path,
        )
        return str(url)