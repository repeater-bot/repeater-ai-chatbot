from fastapi import Query

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/rematch/{path:path}",
    name = "workspace.rematch"
)
async def rematch(
    path: str,
    pattern: str = Query(...)
):
    """Match one workspace path against a regular expression."""
    return await get_data_client().rematch(path, pattern)
