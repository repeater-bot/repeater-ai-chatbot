from pathlib import Path

from pydantic import BaseModel, Field

from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client


@ToolsCaller.register
class RealspaceUploadToWorkspace(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="Real source file path; must be inside the realspace whitelist.")
        workspace_path: str | None = Field(
            default = None,
            description = "Destination workspace path; null uses the source basename."
        )

    name = "realspace_upload_to_workspace"
    description = "Read a real file and upload its bytes into the workspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        data = await get_realspace_client("realspace_upload_to_workspace").get_file(args.path)
        destination = args.workspace_path or Path(args.path).name
        data_client = RuntimeContainer.get_runtime().data_client
        size = await data_client.write_file(destination, data)
        return {
            "source": args.path,
            "destination": destination,
            "size": size,
        }
