from fastapi import Query

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/glob/{path:path}",
    name = "workspace.glob"
)
async def glob(
    path: str,
    pattern: str = Query(...),
    recursive: bool = Query(False)
):
    """Match a glob pattern below a workspace directory."""
    return await get_data_client().glob(
        path = path,
        pattern = pattern,
        recursive = recursive
    )
