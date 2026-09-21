from pydantic import ValidationError
from ..data_manager import ProgramDataManager as DataManager
from .object import ProgramData
from loguru import logger

class ProgramDataManager(DataManager):
    async def load(self, user_id: str, branch_id: str | None = None) -> ProgramData:
        user_configs = await super().load(
            user_id = user_id,
            branch_id = branch_id
        )
        try:
            user_configs = ProgramData(**user_configs)
        except ValidationError as e:
            logger.error(
                "Invalid user configs for user {user_id}: {error}",
                user_id = user_id,
                error = str(e)
            )
            raise
        return user_configs
    
    async def save(self, user_id: str, branch_id: str | None = None, data: ProgramData | None = None) -> None:
        if data is None:
            data = ProgramData()
        await super().save(
            user_id = user_id,
            branch_id = branch_id,
            data = data.model_dump(
                exclude_none = True
            )
        )