from .....special_exception import HTTPException

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.post(
    "/mkdir/{path:path}",
    name = "workspace.mkdir"
)
async def mkdir(path: str) -> str:
    """Create a directory, including missing parents."""
    if not path.strip("/"):
        raise HTTPException(
            status_code = 403,
            detail = "Cannot create the root directory"
        )

    return await get_data_client().mkdir(path)
