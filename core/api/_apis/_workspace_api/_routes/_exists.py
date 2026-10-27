from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/exists/{path:path}",
    name = "workspace.exists"
)
async def exists(path: str) -> bool:
    """Return whether a workspace path exists."""
    return await get_data_client().exists(path)
