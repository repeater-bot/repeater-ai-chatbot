from pydantic import BaseModel, Field

from .....runtime_container import RuntimeContainer
from ....framework import ToolsCaller, ToolPackage, RuntimePackage


@ToolsCaller.register
class SQLiteOpen(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="Filesystem path of an existing SQLite database.")

    name = "workspace_sqlite_open"
    description = "Open an existing SQLite database and return its access id."

    async def call(self, args: Params, runtime: RuntimePackage):
        client = RuntimeContainer.get_runtime().data_client
        return (await client.open_sqlite(args.path)).model_dump()


