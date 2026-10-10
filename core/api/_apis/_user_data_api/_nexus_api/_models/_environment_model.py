from pydantic import BaseModel
from ......user_data_managers.user_config_manager import UserConfigs

class EnvironmentModel(BaseModel):
    context: list
    prompt: str
    config: UserConfigs