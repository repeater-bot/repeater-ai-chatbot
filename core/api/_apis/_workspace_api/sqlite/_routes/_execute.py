from fastapi.responses import ORJSONResponse

from .._requests import ExecuteSQLiteRequest
from .._router import sqlite_router
from .._service import sqlite_manager


@sqlite_router.post(
    "/{sqlite_id}/execute",
    name = "sqlite.execute"
)
async def execute_sqlite(sqlite_id: str, request: ExecuteSQLiteRequest):
    """Execute one SQL statement against an opened SQLite database."""
    result = await sqlite_manager.execute(
        sqlite_id,
        request.sql,
        request.params
    )
    return ORJSONResponse(content = result)
