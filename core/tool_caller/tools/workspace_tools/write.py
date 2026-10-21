from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class WorkspaceWrite(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the file to write.")
        content: str = Field(..., description="The content to write to the file.")    

    name = "workspace.write"
    description = "Write text to a workspace file, creating it if missing. Returns the number of bytes written."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.write_file(args.path, args.content.encode("utf-8"))