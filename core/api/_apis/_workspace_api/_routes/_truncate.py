from fastapi import Query

from .....special_exception import HTTPException

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.post(
    "/truncate/{path:path}",
    name = "workspace.truncate"
)
async def truncate(
    path: str,
    size: int = Query(..., description = "The target size in bytes.")
) -> int:
    """Truncate or extend a workspace file to an exact byte size."""
    if not path.strip("/"):
        raise HTTPException(
            status_code = 400,
            detail = "path cannot be empty"
        )
    if size < 0:
        raise HTTPException(
            status_code = 400,
            detail = "size must not be negative"
        )

    return await get_data_client().truncate(path, size)
