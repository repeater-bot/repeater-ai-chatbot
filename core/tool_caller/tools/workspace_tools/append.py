import base64

from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceAppend(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to append to.")
        data: str = Field(..., description="Base64-encoded bytes to append.")

    name = "workspace_append"
    description = "Append Base64-encoded bytes to a workspace file, creating it if missing."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.append(
            args.path,
            base64.b64decode(args.data, validate = True)
        )
