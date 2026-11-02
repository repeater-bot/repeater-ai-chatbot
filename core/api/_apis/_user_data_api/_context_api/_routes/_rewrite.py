from ......repeater_main import RepeaterMain
from .._router import context_router
from fastapi.responses import (
    ORJSONResponse
)
from ......special_exception import HTTPException
from loguru import logger

from .._requests import (
    RewriteContext
)

@context_router.post("/rewrite/{user_id}")
async def rewrite_context(user_id: str, rewrite_context: RewriteContext):
    """
    Endpoint for rewriting context

    Args:
        user_id (str): User ID
        rewrite_context (RewriteContext): Context to rewrite

    Returns:
        ORJSONResponse: New context
    """
    server = RepeaterMain.get_now_server()

    # 从context_loader中加载用户ID为user_id的上下文
    context_loader = server.core.get_context_loader()
    context = await context_loader.load_context(user_id)

    # 检查索引是否在上下文范围内
    if abs(rewrite_context.index) < len(context.context_list):
        # 重新写入上下文]
        context.rewrite(rewrite_context.content, rewrite_context.index)
        await context_loader.save(user_id, context)
    else:
        raise HTTPException(detail="Index out of range", status_code=400)
    
    logger.info(
        "Rewrite {count} Context",
        user_id = user_id,
        count = abs(rewrite_context.index)
    )
    
    # 返回ORJSONResponse，新的上下文内容
    return ORJSONResponse(context)