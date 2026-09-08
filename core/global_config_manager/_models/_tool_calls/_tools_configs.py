from pydantic import BaseModel, Field
from .tools_configs import (
    HTTPRequests,
    SystemInfo,
    HorizontalToolConfig
)

class ToolsConfigs(BaseModel):
    http_requests: HTTPRequests = Field(default_factory=HTTPRequests)
    system_info: SystemInfo = Field(default_factory=SystemInfo)
    horizontal: HorizontalToolConfig = Field(default_factory=HorizontalToolConfig)