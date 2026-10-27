from fastapi.responses import Response

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/get_file/{path:path}",
    name = "workspace.get_file"
)
async def get_file(path: str):
    """Return a workspace file as raw bytes."""
    data = await get_data_client().get_file(path)
    return Response(
        content = data,
        media_type = "application/octet-stream",
        status_code = 200
    )
