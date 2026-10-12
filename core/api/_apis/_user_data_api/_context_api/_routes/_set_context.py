from ......repeater_main import RepeaterMain
from .._router import context_router
from fastapi.responses import (
    PlainTextResponse,
)
from ......user_data_managers.context import ContentUnit, Context
from loguru import logger

@context_router.put("/set/{user_id}")
async def set_context(user_id: str, context: list[ContentUnit]):
    """
    Endpoint for setting context

    Args:
        user_id (str): User ID
        context (list[ContentUnit]): Context to set
    
    Returns:
        PlainTextResponse: Success message
    """
    server = RepeaterMain.get_now_server()

    # 从chat.context_manager中加载用户ID为user_id的上下文
    context_loader = server.core.get_context_loader()
    ctx = Context(
        context_list = context
    )
    await context_loader.save(user_id, ctx)

    logger.info("Set Context", user_id = user_id)

    # 返回JSON格式的上下文
    return PlainTextResponse("Success")