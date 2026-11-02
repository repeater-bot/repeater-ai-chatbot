from ......repeater_main import RepeaterMain
from .._router import context_router
from fastapi import Query
from fastapi.responses import (
    ORJSONResponse,
)
from loguru import logger

@context_router.get("/get_pairs/{user_id}")
@context_router.get("/get_pairs/{user_id}.json")
async def get_context_pairs(
    user_id: str,
    branch_id: str | None = Query(None),
):
    """
    Endpoint for getting context pairs

    Args:
        user_id (str): User ID
        branch_id (str, optional): Branch ID. Defaults to None.
    
    Returns:
        ORJSONResponse: User context
    """
    server = RepeaterMain.get_now_server()
    runtime = server.runtime

    # 从chat.context_manager中加载用户ID为user_id的上下文
    context_loader = server.core.get_context_loader()
    context = await context_loader.load_context(
        user_id,
        branch_id = branch_id
    )
    context_pairs = context.split_to_pairs()

    if branch_id is None:
        logger.info("Get Active Context Pairs", user_id = user_id)
    else:
        logger.info("Get Context {branch_id} Pairs", user_id = user_id, branch_id = branch_id)

    # 返回JSON格式的上下文
    return ORJSONResponse(
        {
            "context_pairs": [[pair.to_content() for pair in context_pair] for context_pair in context_pairs],
            "length": len(context_pairs),
            "context_length": len(context),
            "total_character_length": context.total_length
        }
    )