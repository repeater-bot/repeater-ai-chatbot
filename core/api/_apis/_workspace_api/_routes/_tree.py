from fastapi import Query

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/tree/{path:path}",
    name = "workspace.tree"
)
async def tree(
    path: str,
    max_depth: int = Query(-1)
) -> dict:
    """Return the nested node tree below a workspace path."""
    return await get_data_client().tree(
        path = path,
        max_depth = max_depth
    )
