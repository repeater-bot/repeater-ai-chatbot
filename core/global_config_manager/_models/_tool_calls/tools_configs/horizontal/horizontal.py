from pydantic import BaseModel, Field
from .user_info import UserInfo

class HorizontalToolConfig(BaseModel):
    """
    Horizontal tool configuration
    """
    servers: dict[str, str] = Field(default_factory=dict)
    user_id: str = Field(default="")
    user_info: UserInfo = Field(default_factory=UserInfo)