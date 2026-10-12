from ......repeater_main import RepeaterMain
from .._router import context_router
from ......user_data_managers.context import (
    ContentRole
)
from fastapi.responses import (
    ORJSONResponse
)
from loguru import logger

@context_router.post("/role_mapping/{user_id}")
async def role_mapping(user_id: str, role_map: dict[ContentRole, ContentRole | None]):
    """
    Context role mapping endpoint.

    Args:
        user_id (str): The ID of the user.
        role_map (dict[ContentRole, ContentRole | None]): The role mapping to apply.

    Returns:
        ORJSONResponse: A response indicating the success or failure of the operation.
    """
    server = RepeaterMain.get_now_server()

    context_loader = server.core.get_context_loader()
    context = await context_loader.load_context(user_id)

    context.role_map(role_map)
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