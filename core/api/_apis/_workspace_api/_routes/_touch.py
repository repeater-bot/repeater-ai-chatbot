from .....special_exception import HTTPException

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.post(
    "/touch/{path:path}",
    name = "workspace.touch"
)
async def touch(path: str) -> int:
    """Create a workspace file when missing and update its timing metadata."""
    if not path.strip("/"):
        raise HTTPException(
            status_code = 400,
            detail = "path cannot be empty"
        )

    return await get_data_client().touch(path)
