import httpx

from ....repeater_main import RepeaterMain
from ....global_config_manager import ConfigManager
from ._router import watermark_router
from .request import WatermarkRequest
from ....special_exception import HTTPException
from fastapi.responses import StreamingResponse

@watermark_router.post("/encode")
async def encode_watermark(request: WatermarkRequest):
    server = RepeaterMain.get_now_server()
    runtime = server.runtime
    configs = ConfigManager.get_configs().watermark

    watermark_client = runtime.watermark_client

    async with httpx.AsyncClient(
        transport = runtime.public_only_transport
    ) as client:
        response = await client.get(
            url = request.image,
        )

    if response.status_code != 200:
        return HTTPException(
            status_code = 400,
            detail = "Invalid image url, please check your url."
        )

    stream = watermark_client.encode_text_watermark(
        image = response.content,
        text = request.text or configs.default_image_watermark,
        output_format = request.output_format,
    )

    return StreamingResponse(
        content = stream,
    )

@watermark_router.post("/decode")
async def decode_watermark(request: WatermarkRequest):
    server = RepeaterMain.get_now_server()
    runtime = server.runtime

    watermark_client = runtime.watermark_client
    
    async with httpx.AsyncClient(
        transport = runtime.public_only_transport
    ) as client:
        response = await client.get(
            url = request.image,
        )

    if response.status_code != 200:
        return HTTPException(
            status_code = 400,
            detail = "Invalid image url, please check your url."
        )

    result = await watermark_client.decode_text_watermark(
        image = response.content
    )

    return {
        "text": result
    }