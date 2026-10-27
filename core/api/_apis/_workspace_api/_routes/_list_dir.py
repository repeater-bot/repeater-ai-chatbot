from fastapi import Query

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/list_dir/{path:path}",
    name = "workspace.list_dir"
)
async def list_dir(
    path: str,
    recursive: bool = Query(False)
):
    """List direct children, or all descendants with ``recursive=true``."""
    return await get_data_client().list_dir(
        path = path,
        recursive = recursive
    )
