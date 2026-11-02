from ......repeater_main import RepeaterMain
from .._router import config_router
from fastapi import Query
from fastapi.responses import (
    ORJSONResponse
)
from loguru import logger

@config_router.get("/get/{user_id}")
@config_router.get("/get/{user_id}.json")
async def get_config(
    user_id: str,
    branch_id: str | None = Query(None)
):
    """
    Endpoint for get config
    """
    server = RepeaterMain.get_now_server()

    # 获取用户ID为user_id的配置
    config = await server.core.get_config(user_id = user_id, branch_id = branch_id)

    if branch_id is None:
        logger.info(
            "Get active user config",
            user_id = user_id
        )
    else:
        logger.info(
            "Get {branch_id} user config",
            user_id = user_id,
            branch_id = branch_id
        )

    # 返回配置
    return ORJSONResponse(config.model_dump(exclude_none=True))