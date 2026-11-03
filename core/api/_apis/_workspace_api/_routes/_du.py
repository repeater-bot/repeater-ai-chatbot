from .....clients.data_client import DiskUsage

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/du/{path:path}",
    name = "workspace.du"
)
async def du(path: str) -> DiskUsage:
    """Measure the total size and the entry counts below a workspace path."""
    return await get_data_client().du(path)
