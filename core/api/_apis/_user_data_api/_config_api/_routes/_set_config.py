from ......repeater_main import RepeaterMain
from .._router import config_router
from fastapi.responses import (
    ORJSONResponse,
)
from ......user_data_managers.user_config_manager import (
    UserConfigs
)
from ......special_exception import HTTPException
from .._requests import (
    SetConfigRequest,
    FieldType
)
from loguru import logger

from pydantic import ValidationError

@config_router.put("/set/{user_id}")
async def set_config(user_id: str, request: UserConfigs):
    """
    Set user config

    Args:
        user_id (str): User ID
        request (UserConfigs): User Config Data
    
    Returns:
        ORJSONResponse: User Config Data
    """
    server = RepeaterMain.get_now_server()
    runtime = server.runtime

    await runtime.user_config_manager.save(user_id=user_id, data=request)
    logger.info(
        "Set user config: \n{config}",
        user_id = user_id,
        config = request.model_dump_json(indent=4, ensure_ascii=False, exclude_defaults=True)
    )
    return ORJSONResponse(
        request.model_dump(exclude_defaults=True)
    )

@config_router.put("/set/{user_id}/{key}")
async def set_config_field(user_id: str, key: str, request: SetConfigRequest):
    """
    Endpoint for setting config

    Args:
        user_id (str): User ID
        key (str): Config Key
        request (SetConfigRequest): Config Value
    
    Returns:
        ORJSONResponse: Config
    """
    # 允许的值类型
    match request.type:
        case FieldType.INT:
            value = int(request.value)
        case FieldType.FLOAT:
            value = float(request.value)
        case FieldType.STRING:
            value = str(request.value)
        case FieldType.BOOLEAN:
            value = bool(request.value)
        case FieldType.DICT:
            if not isinstance(request.value, dict):
                raise HTTPException(status_code=400, detail="Value must be a dict.")
            value = request.value
        case FieldType.LIST:
            if not isinstance(request.value, list):
                raise HTTPException(status_code=400, detail="Value must be a list.")
            value = request.value
        case FieldType.RAW:
            value = request.value
        case FieldType.NULL:
            value = None
        case _:
            raise HTTPException(status_code=400, detail="Invalid type.")
    
    server = RepeaterMain.get_now_server()
    runtime = server.runtime
    
    # 读取配置
    config = await runtime.user_config_manager.load(user_id=user_id)
    
    # 更新配置
    if key in type(config).model_fields.keys():
        try:
            setattr(config, key, value)
        except ValidationError as e:
            errors = e.errors()
            text_buffer: list[str] = []
            for error in errors:
                text_buffer.append(f"{'.'.join(error['loc'])}: {error['msg']}")
            raise HTTPException(400, "\n".join(text_buffer))
    else:
        raise HTTPException(400, "Invalid config key")

    # 保存配置
    await runtime.user_config_manager.save(user_id=user_id, data=config)
    
    logger.info(
        "Set user config {key}={value}(type:{value_type})",
        user_id = user_id,
        key = key,
        value = value,
        value_type = request.type
    )

    # 返回新配置内容
    return ORJSONResponse(
        config.model_dump(exclude_defaults=True),
    )