from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/is_dir/{path:path}",
    name = "workspace.is_dir"
)
async def is_dir(path: str) -> bool:
    """Return whether a workspace path is a directory."""
    return await get_data_client().is_dir(path)
