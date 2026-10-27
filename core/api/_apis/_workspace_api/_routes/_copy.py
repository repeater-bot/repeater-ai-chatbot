from .....clients.data_client import CopyResult

from .._client import get_data_client
from .._requests import DestinationRequest
from .._router import workspace_router


@workspace_router.post(
    "/copy/{path:path}",
    name = "workspace.copy"
)
async def copy(
    path: str,
    request: DestinationRequest
) -> CopyResult:
    """Copy a file or directory with fresh file ids and payloads."""
    return await get_data_client().copy(path, request.destination)
