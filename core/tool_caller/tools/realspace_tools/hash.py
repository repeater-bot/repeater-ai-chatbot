from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field


@ToolsCaller.register
class RealspaceHash(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to hash.")
        algorithm: str = Field(
            default="sha256",
            description="Hash algorithm name, for example 'sha256' or 'md5'."
        )

    name = "realspace_hash"
    description = "Compute the digest of a realspace file."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_hash")
        global_runtime = RuntimeContainer.get_runtime()

        return await data_client.hash(
            args.path,
            args.algorithm
        )
