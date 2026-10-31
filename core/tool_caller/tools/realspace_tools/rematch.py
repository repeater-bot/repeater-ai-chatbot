from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceRematch(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The virtual path to match.")
        pattern: str = Field(
            ...,
            description="Python regular expression; re.match is used from the start of the path."
        )

    name = "realspace_rematch"
    description = "Check whether a virtual realspace path matches a regular expression."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_rematch")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.rematch(args.path, args.pattern)
