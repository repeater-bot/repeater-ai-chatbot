import asyncio
from typing import Any
from loguru import logger
from pydantic import ValidationError
from ..data_manager import UserConfigManager
from ._exceptions import *
from ._object import UserConfigs
from ..global_config_manager import ConfigManager as GlobalConfigManager

class ConfigManager(UserConfigManager):
    async def load(self, user_id: str, branch_id: str | None = None):
        user_configs = await super().load(user_id = user_id, branch_id = branch_id)
        try:
            user_configs = UserConfigs(**user_configs)
        except ValidationError as e:
            logger.error(
                "Invalid user configs for user {user_id}: {error}",
                user_id = user_id,
                error = str(e)
            )
            raise ConfigFieldError(e) from e
        return user_configs
    
    async def save(self, user_id: str, branch_id: str | None = None, data: UserConfigs | None = None) -> None:
        if data is None:
            data = UserConfigs()
        await super().save(
            user_id = user_id,
            branch_id = branch_id,
            data = data.model_dump(
                exclude_none = True
            )
        )