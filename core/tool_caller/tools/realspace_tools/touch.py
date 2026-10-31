from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceTouch(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to create or touch.")

    name = "realspace_touch"
    description = "Create an empty realspace file when missing, or refresh its timestamp."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_touch")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.touch(args.path)
