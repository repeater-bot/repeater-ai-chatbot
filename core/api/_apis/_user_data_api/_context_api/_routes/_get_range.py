from ......repeater_main import RepeaterMain
from .._router import context_router
from fastapi import Query
from fastapi.responses import (
    ORJSONResponse
)
from loguru import logger

@context_router.get("/part_of/{user_id}-{begin}-{end}")
@context_router.get("/part_of/{user_id}-{begin}-{end}.json")
async def get_part_of_context(
    user_id: str,
    begin: int | float,
    end: int | float,
    branch_id: str | None = Query(None)
):
    """
    Get part of the context.

    Args:
        user_id (str): The ID of the user.
        begin (int): The begin timestamp of the context.
        end (int): The end timestamp of the context.
        branch_id (str, optional): The ID of the branch. Defaults to None.

    Returns:
        ORJSONResponse: A response indicating the success or failure of the operation.
    """
    server = RepeaterMain.get_now_server()

    context_loader = server.core.get_context_loader()
    context = await context_loader.load_context(
        user_id,
        branch_id = branch_id
    )
    
    time_range = context.time_range(begin, end)

    if branch_id is None:
        logger.info(
            "Get part of active context: {user_id}-{begin}-{end}",
            user_id = user_id,
            begin = begin,
            end = end
        )
    else:
        logger.info(
            "Get part of {branch_id} context: {user_id}-{begin}-{end}",
            user_id = user_id,
            branch_id = branch_id,
            begin = begin,
            end = end
        )

    return ORJSONResponse(
        content=time_range.to_context(),
    )