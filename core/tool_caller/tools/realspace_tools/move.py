from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceMove(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The current path of the file or directory.")
        destination: str = Field(..., description="The new virtual path.")

    name = "realspace_move"
    description = "Move a file or directory in the realspace; file ids and payloads stay unchanged."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_move")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.move(args.path, args.destination)
