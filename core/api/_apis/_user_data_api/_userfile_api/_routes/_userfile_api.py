import asyncio
from ......repeater_main import RepeaterMain
from .._router import user_file_router
from fastapi.responses import (
    StreamingResponse
)
from loguru import logger
from io import BytesIO
from .._auxiliary import (
    make_user_file
)


@user_file_router.get("/file/{user_id}.zip")
async def get_userdata_file(user_id: str):
    """
    Endpoint for getting userdata file

    Args:
        user_id (str): User ID

    Returns:
        Response: File Response
    """
    # 创建虚拟文件缓冲区
    buffer = BytesIO()
    server = RepeaterMain.get_now_server()
    context_loader = server.core.get_context_loader()
    context = await context_loader.load_context(user_id = user_id)
    prompt = await server.runtime.prompt_manager.load(user_id = user_id, default = "")
    config = await server.runtime.user_config_manager.load(user_id = user_id)
    program_data_manager = server.runtime.program_data_manager
    program_data = await program_data_manager.load(user_id = user_id)
    
    await asyncio.to_thread(
        make_user_file,
        file = buffer,
        context = context,
        prompt = prompt,
        user_configs = config,
        program_data = program_data
    )

    logger.info(
        "Downloaded userdata file",
        user_id = user_id
    )

    # 获取文件大小
    buffer.seek(0, 2)
    file_size = buffer.tell()
    buffer.seek(0)

    # 返回zip文件
    return StreamingResponse(
        buffer,
        media_type = "application/octet-stream",
        headers = {
            "Content-Length": str(file_size),
        }
    )