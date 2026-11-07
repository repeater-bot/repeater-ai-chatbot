import base64

from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceAppendText(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to append to.")
        text: str = Field(..., description="Text to append.")
        encoding: str = Field("utf-8", description="Encoding of the file.")

    name = "workspace_append_text"
    description = "Append text to a workspace file, creating it if missing."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.append(
            args.path,
            args.text.encode(args.encoding),
        )
