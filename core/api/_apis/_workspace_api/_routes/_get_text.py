from fastapi import Query
from fastapi.responses import PlainTextResponse

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/get_text/{path:path}",
    name = "workspace.get_text"
)
async def get_text(
    path: str,
    text_encoding: str = Query("utf-8")
):
    """Return a workspace file decoded as text."""
    return PlainTextResponse(
        content = await get_data_client().get_text(
            path,
            text_encoding = text_encoding
        ),
        status_code = 200
    )
