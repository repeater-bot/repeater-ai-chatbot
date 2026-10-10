from ......repeater_main import RepeaterMain
from .._router import context_router
from ......user_data_managers.context import (
    ContentUnit,
    ContentRole
)
from fastapi.responses import (
    ORJSONResponse
)
from loguru import logger

@context_router.post("/inject/{user_id}")
async def inject_context(user_id: str, request: ContentUnit):
    """
    Injects a user's content into the context.

    Args:
        user_id (str): The ID of the user.
        request (ContentUnit): The content to inject.

    Returns:
        ORJSONResponse: A response indicating the success or failure of the operation.
    """
    server = RepeaterMain.get_now_server()

    context_loader = server.core.get_context_loader()
    context = await context_loader.load_context(user_id)

    context.append(content = request)
    await context_loader.save(user_id, context)
    logger.info(
        "User {user_id} injected context",
        user_id = user_id
    )
    return ORJSONResponse(
        {
            "status": "success",
            "context": context.to_context()
        }
    )