from ......special_exception import HTTPException
from ......repeater_main import RepeaterMain
from .._router import context_router
from ......user_data_managers.context import (
    Context
)
from fastapi import Form
from fastapi.responses import (
    ORJSONResponse
)
from loguru import logger

@context_router.post("/withdraw/{user_id}")
async def withdraw_context(user_id: str, context_pair_num: int = Form(1, gt=0), paired: bool = Form(True)):
    """
    Endpoint for withdrawing context

    Args:
        user_id (str): The user ID
        length (int | None): The number of messages to withdraw

    Returns:
        ORJSONResponse: New context
    """
    server = RepeaterMain.get_now_server()

    # 从context_loader中加载用户ID为user_id的上下文
    context_loader = server.core.get_context_loader()
    context = await context_loader.load_context(user_id)
    pop_items: list[Context] = []

    if paired:
        try:
            for _ in range(context_pair_num):
                pop_items.append(
                    context.withdraw()
                )
        except (ValueError, IndexError) as e:
            raise HTTPException(400, str(e)) from e
        
        pop_context = Context()
        for item in pop_items[::-1]:
            pop_context.context_list.extend(
                item.context_list
            )
    else:
        try:
            pop_context_list = context.pop_last_n(context_pair_num)
            pop_context = Context(context_list = pop_context_list)
        except (ValueError, IndexError) as e:
            raise HTTPException(str(e), 400) from e
    
    # 返回ORJSONResponse，新的上下文内容
    await context_loader.save(user_id, context)
    logger.info(
        "User {user_id} withdraw {pop_context_len} context pairs",
        user_id = user_id,
        pop_context_len = len(pop_context)
    )
    return ORJSONResponse(
        {
            "status": "success",
            "deleted": len(pop_context),
            "deleted_context": pop_context.to_context(),
            "delete_context_pair": len(pop_items),
            "context": context.to_context(),
        }
    )