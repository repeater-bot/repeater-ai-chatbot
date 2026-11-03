import base64
from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field
from typing import Literal

@ToolsCaller.register
class WorkspaceGetUrl(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the file to read.")

    name = "workspace_get_url"
    description = "Get the URL of a file in the workspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        url = await data_client.get_file_url(
            args.path,
        )
        return str(url)