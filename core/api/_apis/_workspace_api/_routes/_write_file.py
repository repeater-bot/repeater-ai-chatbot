from fastapi import File, UploadFile

from .._client import get_data_client
from .._router import workspace_router


@workspace_router.post(
    "/write_file/{path:path}",
    name = "workspace.write_file"
)
async def write_file(
    path: str,
    file: UploadFile = File(...)
):
    """Write an uploaded file into the workspace."""
    data = await file.read()
    return await get_data_client().write_file(
        path = path,
        data = data,
        filename = file.filename,
        content_type = file.content_type or "application/octet-stream"
    )
