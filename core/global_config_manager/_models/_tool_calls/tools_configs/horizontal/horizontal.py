from pydantic import BaseModel, Field
from .user_info import UserInfo

class HorizontalToolConfig(BaseModel):
    """
    Horizontal tool configuration
    """
    servers: dict[str, str] = Field(default_factory=dict)
    user_id: str = Field(default="")
    with_now_user_id: bool = Field(default=True)
    user_info: UserInfo = Field(default_factory=UserInfo)