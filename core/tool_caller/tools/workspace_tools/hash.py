from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceHash(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The file path to hash.")
        algorithm: str = Field(
            default="sha256",
            description="Hash algorithm name, for example 'sha256' or 'md5'."
        )

    name = "workspace_hash"
    description = "Compute the digest of a workspace file."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        return await data_client.hash(
            args.path,
            args.algorithm
        )
