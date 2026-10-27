import asyncio
from ......repeater_main import RepeaterMain
from .._router import user_file_router
from fastapi.responses import (
    StreamingResponse
)
from loguru import logger
from io import BytesIO
from .._auxiliary import package_user_space


@user_file_router.get("/package_space/{user_id}.zip")
async def get_userdata_file(user_id: str):
    """
    Endpoint for package user space to zip file

    Args:
        user_id (str): User ID

    Returns:
        Response: File stream
    """
    # 创建虚拟文件缓冲区
    buffer = BytesIO()
    server = RepeaterMain.get_now_server()
    context_loader = server.core.get_context_loader()
    prompt_manager = server.runtime.prompt_manager
    config_manager = server.runtime.user_config_manager
    program_data_manager = server.runtime.program_data_manager
    
    await package_user_space(
        user_id = user_id,
        context_loader = context_loader,
        prompt_manager = prompt_manager,
        config_manager = config_manager,
        program_data_manager = program_data_manager,
        file = buffer
    )

    logger.info(
        "User {user_id} package space",
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