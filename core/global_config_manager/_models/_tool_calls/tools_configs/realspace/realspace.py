from pydantic import BaseModel, Field
from .whitelist_unit import RealspaceWhitelistUnit

class RealspaceConfigs(BaseModel):
    dir_auto_sandbox: bool = True
    whitelist: dict[str, RealspaceWhitelistUnit] = Field(default_factory=dict)
