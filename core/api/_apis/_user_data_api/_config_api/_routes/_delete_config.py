from ......repeater_main import RepeaterMain
from .._router import config_router
from typing import Any
from fastapi.responses import (
    ORJSONResponse,
    PlainTextResponse
)
from ......user_data_managers.user_config_manager import (
    UserConfigs
)
from ......special_exception import (
    HTTPException
)
from .._requests import (
    SetConfigRequest
)
from fastapi import (
    Form
)
from loguru import logger

from pydantic import BaseModel, ValidationError

@config_router.put("/delkey/{user_id}")
async def delete_config_field(user_id: str, key: str = Form(...)):
    """
    Endpoint for delkey config

    Parameters:
        user_id (str): User ID
        key (str): User config key

    Returns:
        ORJSONResponse: New config content
    """
    server = RepeaterMain.get_now_server()
    runtime = server.runtime

    # 读取配置
    config = await runtime.user_config_manager.load(user_id=user_id)
    
    # 更新配置
    try:
        if key in type(config).model_fields.keys():
            setattr(
                config,
                key,
                type(config).model_fields[key].default
            )
        else:
            raise HTTPException(400, "Invalid config key")
    except ValidationError as e:
        raise HTTPException(500, "The default value is not one of the valid values for this field and can not be assigned.")

    # 保存配置
    await runtime.user_config_manager.save(user_id=user_id, data=config)

    logger.info("Delete user config field: {key}", user_id = user_id, key = key)

    # 返回新配置内容
    return ORJSONResponse(config.model_dump(exclude_defaults=True))