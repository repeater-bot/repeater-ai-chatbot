from pydantic import BaseModel, Field

from .....runtime_container import RuntimeContainer
from ....framework import ToolsCaller, ToolPackage, RuntimePackage


@ToolsCaller.register
class SQLiteClose(ToolPackage):
    class Params(BaseModel):
        sqlite_id: str = Field(..., description="Access id to close.")

    name = "workspace_sqlite_close"
    description = "Close an opened SQLite database and invalidate its access id."

    async def call(self, args: Params, runtime: RuntimePackage):
        client = RuntimeContainer.get_runtime().data_client
        await client.close_sqlite(args.sqlite_id)
        return {
            "id": args.sqlite_id,
            "closed": True,
        }


