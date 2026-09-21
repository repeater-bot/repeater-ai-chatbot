from .._router import merged_user_data_router
from fastapi.responses import (
    ORJSONResponse
)
from fastapi import (
    Form
)
from loguru import logger
from ..._user_data_type import UserDataType, get_manager

@merged_user_data_router.put("/{user_data_type}/bind/{user_id}")
async def bind_branch(user_data_type: UserDataType, user_id: str, dst_branch_id: str = Form(...)):
    """
    Bind branch

    Args:
        user_id (str): User ID
        dst_branch_id (str): Destination branch ID
    """
    manager = get_manager(user_data_type)
    await manager.bind(
        user_id = user_id,
        dst_branch_id = dst_branch_id
    )

    logger.info(
        "Bind {user_data_type} branch from active branch to {branch_id}",
        user_id = user_id,
        branch_id = dst_branch_id,
        user_data_type = user_data_type.value
    )

    return ORJSONResponse({"status": "success"})


@merged_user_data_router.put("/{user_data_type}/bind_from/{user_id}")
async def bind_branch_from(user_data_type: UserDataType, user_id: str, src_branch_id: str = Form(...)):
    """
    Bind branch from another branch

    Args:
        user_id (str): User ID
        src_branch_id (str): Source branch ID
    """
    manager = get_manager(user_data_type)
    await manager.bind(
        user_id = user_id,
        branch_id = src_branch_id,
        dst_branch_id = await manager.get_active_branch_id(user_id),
    )

    logger.info(
        "Bind {user_data_type} branch from {branch_id} to active branch",
        user_id = user_id,
        branch_id = src_branch_id,
        user_data_type = user_data_type.value
    )

    return ORJSONResponse({"status": "success"})