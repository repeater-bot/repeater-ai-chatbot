from fastapi.responses import ORJSONResponse

from .._router import sqlite_router
from .._service import sqlite_manager


@sqlite_router.delete(
    "/{sqlite_id}",
    name = "sqlite.close"
)
async def close_sqlite(sqlite_id: str):
    """Close an opened SQLite database and invalidate its access id."""
    await sqlite_manager.close(sqlite_id)
    return ORJSONResponse(
        content = {
            "id": sqlite_id,
            "closed": True,
        }
    )
