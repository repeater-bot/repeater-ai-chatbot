from fastapi import Query

from .....clients.data_client import HashResult

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/hash/{path:path}",
    name = "workspace.hash"
)
async def hash(
    path: str,
    algorithm: str = Query("sha256")
) -> HashResult:
    """Return the digest of a workspace file."""
    return await get_data_client().hash(
        path = path,
        algorithm = algorithm
    )
