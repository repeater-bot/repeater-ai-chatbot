from fastapi.responses import ORJSONResponse

from .._requests import CreateSQLiteRequest
from .._router import sqlite_router
from .._service import sqlite_manager


@sqlite_router.post(
    "/open",
    name = "sqlite.open"
)
async def open_sqlite(request: CreateSQLiteRequest):
    """Open an existing SQLite database and return its access id."""
    session_id, path = await sqlite_manager.open(request.path)
    return ORJSONResponse(
        content = {
            "id": session_id,
            "path": path,
        }
    )
