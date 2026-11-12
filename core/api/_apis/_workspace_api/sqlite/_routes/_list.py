from fastapi.responses import ORJSONResponse

from .._router import sqlite_router
from .._service import sqlite_manager


@sqlite_router.get(
    "/list",
    name = "sqlite.list"
)
async def list_sqlite():
    """List every SQLite database currently open on DataServer."""
    return ORJSONResponse(
        content = await sqlite_manager.list_open()
    )
