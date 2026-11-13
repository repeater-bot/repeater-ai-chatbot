from typing import Any

from pydantic import BaseModel, Field

from .....runtime_container import RuntimeContainer
from ....framework import ToolsCaller, ToolPackage, RuntimePackage


@ToolsCaller.register
class SQLiteExecute(ToolPackage):
    class Params(BaseModel):
        sqlite_id: str = Field(..., description="Access id returned by sqlite_create or sqlite_open.")
        sql: str = Field(..., description="One SQLite statement to execute.")
        params: list[Any] | dict[str, Any] | None = Field(
            default = None,
            description = "Optional positional or named parameters."
        )

    name = "workspace_sqlite_execute"
    description = "Execute one SQL statement against an opened SQLite database."

    async def call(self, args: Params, runtime: RuntimePackage):
        client = RuntimeContainer.get_runtime().data_client
        return (
            await client.execute_sqlite(args.sqlite_id, args.sql, args.params)
        ).model_dump()


