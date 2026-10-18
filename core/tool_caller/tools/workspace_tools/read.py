import base64
from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class WorkspaceRead(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the file to read.")
        base64_encode: bool = Field(False, description="Whether to encode the file content as base64.")

    name = "workspace_read"
    description = "Read a file from the workspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        result = await data_client.get_file(args.path)
        if args.base64_encode:
            encoded_result = base64.b64encode(result).decode("utf-8")
        else:
            encoded_result = result.decode("utf-8")

        return encoded_result