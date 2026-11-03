import base64
import binascii

from .....special_exception import HTTPException

from .._client import get_data_client
from .._requests import EditRequest
from .._router import workspace_router


@workspace_router.post(
    "/edit/{path:path}",
    name = "workspace.edit"
)
async def edit(path: str, request: EditRequest) -> int:
    """Replace the ``[start, end)`` byte range of a workspace file."""
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

    try:
        data = base64.b64decode(
            "".join(request.data.split()),
            validate = True
        )
    except (binascii.Error, ValueError) as e:
        raise HTTPException(
            status_code = 400,
            detail = f"data must be valid Base64: {e}"
        ) from e

    return await get_data_client().edit(
        path = path,
        data = data,
        start = request.start,
        end = request.end
    )
