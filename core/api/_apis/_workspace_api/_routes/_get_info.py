from .....clients.data_client import FileInfo

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/get_info/{path:path}",
    name = "workspace.get_info"
)
async def get_info(path: str) -> FileInfo:
    """Return metadata for a workspace file."""
    return await get_data_client().get_info(path)
