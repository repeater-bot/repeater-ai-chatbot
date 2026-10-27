from .._router import merged_user_data_router
from fastapi.responses import (
    PlainTextResponse
)
from loguru import logger
from ..._user_data_type import UserDataType, get_manager

@merged_user_data_router.get("/{user_data_type}/active/{user_id}")
async def get_active_branch_id(user_data_type: UserDataType, user_id: str):
    """
    Endpoint for getting active branch ID

    Args:
        user_id (str): User ID

    Returns:
        PlainTextResponse: Now Branch ID
    """
    # 获取用户ID为user_id的提示词分支ID
    manager = get_manager(user_data_type)
    branch_id = await manager.get_active_branch_id(user_id)

    logger.info(
        "Get {user_data_type} active branch id",
        user_id = user_id,
        user_data_type = user_data_type.value
    )

    # 返回分支ID
    return PlainTextResponse(branch_id)