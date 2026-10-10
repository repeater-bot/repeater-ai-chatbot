from ......repeater_main import RepeaterMain
from .._router import context_router
from ......user_data_managers.context import (
    ContentUnit
)
from fastapi.responses import (
    ORJSONResponse
)
from loguru import logger

@context_router.get("/part_of/{user_id}-{begin}-{end}")
@context_router.get("/part_of/{user_id}-{begin}-{end}.json")
async def get_part_of_context(user_id: str, begin: int | float, end: int | float):
    """
    Get part of the context.

    Args:
        user_id (str): The ID of the user.
        begin (int): The begin timestamp of the context.
        end (int): The end timestamp of the context.

    Returns:
        ORJSONResponse: A response indicating the success or failure of the operation.
    """
    server = RepeaterMain.get_now_server()

    context_loader = server.core.get_context_loader()
    context = await context_loader.load_context(user_id)
    
    time_range = context.time_range(begin, end)

    return ORJSONResponse(
        content=time_range.to_context(),
    )