from ......repeater_main import RepeaterMain
from .._router import context_router
from fastapi import Query
from fastapi.responses import (
    ORJSONResponse,
)
from loguru import logger

@context_router.get("/get/{user_id}")
@context_router.get("/get/{user_id}.json")
async def get_context(
    user_id: str,
    branch_id: str | None = Query(None),
):
    """
    Endpoint for getting context

    Args:
        user_id (str): User ID
        branch_id (str, optional): Branch ID
    
    Returns:
        ORJSONResponse: User context
    """
    server = RepeaterMain.get_now_server()
    runtime = server.runtime

    # 从chat.context_manager中加载用户ID为user_id的上下文
    context_loader = server.core.get_context_loader()
    context = await context_loader.load_context(
        user_id,
        branch_id = branch_id,
    )

    if branch_id is None:
        logger.info("Get Active Context", user_id = user_id)
    else:
        logger.info("Get Context {branch_id}", user_id = user_id, branch_id = branch_id)

    # 返回JSON格式的上下文
    return ORJSONResponse(context.to_context())