from .....clients.data_client import MoveResult

from .._client import get_data_client
from .._requests import DestinationRequest
from .._router import workspace_router


@workspace_router.post(
    "/move/{path:path}",
    name = "workspace.move"
)
async def move(
    path: str,
    request: DestinationRequest
) -> MoveResult:
    """Move a file or directory without changing file ids or payloads."""
    return await get_data_client().move(path, request.destination)
