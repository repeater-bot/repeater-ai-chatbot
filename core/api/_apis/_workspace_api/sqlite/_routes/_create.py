from fastapi.responses import ORJSONResponse

from .._requests import CreateSQLiteRequest
from .._router import sqlite_router
from .._service import sqlite_manager


@sqlite_router.post(
    "/create",
    name = "sqlite.create"
)
async def create_sqlite(request: CreateSQLiteRequest):
    """Create or open a SQLite database and return its access id."""
    session_id, path = await sqlite_manager.create(request.path)
    return ORJSONResponse(
        content = {
            "id": session_id,
            "path": path,
        }
    )
