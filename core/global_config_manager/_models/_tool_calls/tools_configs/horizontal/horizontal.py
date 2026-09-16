from pydantic import BaseModel, Field
from .user_info import UserInfo
from .user_id_strategies import UserIdStrategies

class HorizontalToolConfig(BaseModel):
    """
    Horizontal tool configuration
    """
    servers: dict[str, str] = Field(default_factory=dict)
    local_id: str = ""
    user_id_strategy: UserIdStrategies = UserIdStrategies.SEPARATE
    role_name: str | None = None
    user_info: UserInfo = Field(default_factory=UserInfo)