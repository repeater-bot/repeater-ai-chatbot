import orjson
from ._router import image_router
from typing import AsyncGenerator
from fastapi import Request as FastAPI_Request
from fastapi.responses import ORJSONResponse, StreamingResponse
from .....call_api.image import (
    ImagesResponse,
    PartialImageEvent,
    CompletedImageEvent
)
from .....core.image import (
    Request,
    generate_image as generate_image_core
)

@image_router.post("/generate/{user_id}")
async def generate_image(
    user_id: str,
    request: Request,
    fastapi_request: FastAPI_Request
):
    """
    Generate image from prompt.
    """
    result = await generate_image_core(
        user_id,
        request,
        fastapi_request
    )

    if isinstance(result, ImagesResponse):
        return ORJSONResponse(
            status_code = 200,
            content = result.model_dump()
        )
    else:
        async def stream_to_json(result: AsyncGenerator[PartialImageEvent | CompletedImageEvent, None]) -> AsyncGenerator[bytes, None]:
            async for event in result:
                yield orjson.dumps(event.model_dump()) + b"\n"
        
        return StreamingResponse(
            content = stream_to_json(result),
        )