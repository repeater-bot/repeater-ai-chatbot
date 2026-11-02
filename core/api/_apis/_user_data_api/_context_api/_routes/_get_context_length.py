from ......repeater_main import RepeaterMain
from .._router import context_router
from fastapi import Query
from fastapi.responses import (
    ORJSONResponse
)
from loguru import logger

@context_router.get("/length/{user_id}")
async def get_context_length(
    user_id: str,
    branch_id: str | None = Query(None)
):
    """
    Endpoint for getting context

    Args:
        user_id (str): The user ID
        branch_id (str, optional): The branch ID. Defaults to None.
    
    Returns:
        ORJSONResponse: The JSON response containing the context length
    """
    server = RepeaterMain.get_now_server()

    # 从chat.context_manager中加载用户ID为user_id的上下文
    context_loader = server.core.get_context_loader()
    context = await context_loader.load_context(user_id, branch_id = branch_id)

    if branch_id is None:
        logger.info("Get Active Context length", user_id = user_id)
    else:
        logger.info("Get Context {branch_id} length", user_id = user_id, branch_id = branch_id)

    # 返回ORJSONResponse，包含上下文的总长度和上下文的长度
    return ORJSONResponse(
        {
            "total_context_length": context.total_length,
            "context_length": context.context_item_length,
            "average_content_length": context.average_length
        }
    )