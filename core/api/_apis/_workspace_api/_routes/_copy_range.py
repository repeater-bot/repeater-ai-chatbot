from .....clients.data_client import CopyRangeResult
from .....special_exception import HTTPException

from .._client import get_data_client
from .._requests import CopyRangeRequest
from .._router import workspace_router


@workspace_router.post(
    "/copy_range/{path:path}",
    name = "workspace.copy_range"
)
async def copy_range(
    path: str,
    request: CopyRangeRequest
) -> CopyRangeResult:
    """Copy the ``[start, end)`` byte range of a workspace file."""
    if not path.strip("/"):
        raise HTTPException(
            status_code = 400,
            detail = "path cannot be empty"
        )
    if request.start < 0:
        raise HTTPException(
            status_code = 400,
            detail = "start must not be negative"
        )
    if request.end < 0:
        raise HTTPException(
            status_code = 400,
            detail = "end must not be negative"
        )
    if request.end < request.start:
        raise HTTPException(
            status_code = 400,
            detail = "end must not be less than start"
        )

    return await get_data_client().copy_range(
        path = path,
        destination = request.destination,
        start = request.start,
        end = request.end
    )
