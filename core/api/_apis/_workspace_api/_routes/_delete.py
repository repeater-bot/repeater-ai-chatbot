from fastapi import Query

from .....clients.data_client import DeleteResult
from .....special_exception import HTTPException

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.delete(
    "/delete/{path:path}",
    name = "workspace.delete"
)
async def delete(
    path: str,
    recursive: bool = Query(False)
) -> DeleteResult:
    """Delete a workspace file or directory."""
    if not path.strip("/"):
        raise HTTPException(
            status_code = 403,
            detail = "Cannot delete the root directory"
        )

    return await get_data_client().delete(
        path = path,
        recursive = recursive
    )
