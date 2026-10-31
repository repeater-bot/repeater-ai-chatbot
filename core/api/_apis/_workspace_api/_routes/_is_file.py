from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/is_file/{path:path}",
    name = "workspace.is_file"
)
async def is_file(path: str) -> bool:
    """Return whether a workspace path is a file."""
    return await get_data_client().is_file(path)
