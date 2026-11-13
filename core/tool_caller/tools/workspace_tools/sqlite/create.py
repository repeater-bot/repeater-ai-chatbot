from pydantic import BaseModel, Field

from .....runtime_container import RuntimeContainer
from ....framework import ToolsCaller, ToolPackage, RuntimePackage


@ToolsCaller.register
class SQLiteCreate(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="Filesystem path for the new SQLite database.")

    name = "workspace_sqlite_create"
    description = "Create a new SQLite database and return its access id."

    async def call(self, args: Params, runtime: RuntimePackage):
        client = RuntimeContainer.get_runtime().data_client
        return (await client.create_sqlite(args.path)).model_dump()


