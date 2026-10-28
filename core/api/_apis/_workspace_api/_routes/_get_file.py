from fastapi import Request
from fastapi.responses import Response

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.get(
    "/get_file/{path:path}",
    name = "workspace.get_file"
)
async def get_file(path: str, request: Request):
    """Return a workspace file as raw bytes, preserving Range headers."""
    forwarded_headers = {
        name: request.headers[name]
        for name in ("range", "if-range")
        if name in request.headers
    }
    upstream = await get_data_client().get_file_response(
        path,
        headers = forwarded_headers
    )

    response_headers = {
        name: upstream.headers[name]
        for name in (
            "content-range",
            "accept-ranges",
            "content-length",
            "etag",
            "last-modified",
        )
        if name in upstream.headers
    }
    media_type = upstream.headers.get(
        "content-type",
        "application/octet-stream"
    )

    return Response(
        content = upstream.content,
        status_code = upstream.status_code,
        media_type = media_type,
        headers = response_headers
    )
