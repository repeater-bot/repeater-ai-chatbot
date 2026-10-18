from pydantic import BaseModel, Field, field_serializer
from ._tools_configs import ToolsConfigs

class ToolCallsConfigs(BaseModel):
    enabled: bool = True
    registed: set[str] = Field(default_factory=set)
    allowed_by_default: set[str] = Field(default_factory=set)
    result_max_length_for_logs: int | None = 100
    timeout: int | float | None = None
    tool_result_timeout: int | float | None = 60
    tools_configs: ToolsConfigs = Field(default_factory=ToolsConfigs)

    @field_serializer("registed", mode = "plain")
    def registed_serializer(self, value: set[str]) -> list[str]:
        return list(value)
    
    @field_serializer("allowed_by_default", mode = "plain")
    def allowed_by_default_serializer(self, value: set[str]) -> list[str]:
        return list(value)