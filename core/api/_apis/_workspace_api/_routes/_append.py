from fastapi import Request

from .....special_exception import HTTPException

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.post(
    "/append/{path:path}",
    name = "workspace.append"
)
async def append(path: str, request: Request) -> int:
    """Append the raw request body to a workspace file."""
    if not path.strip("/"):
        raise HTTPException(
            status_code = 400,
            detail = "path cannot be empty"
        )

    return await get_data_client().append(
        path = path,
        data = await request.body()
    )
