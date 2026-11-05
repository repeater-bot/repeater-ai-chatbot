from pydantic import BaseModel, Field
from .whitelist_unit import RealspaceWhitelistUnit

class RealspaceConfigs(BaseModel):
    whitelist: list[RealspaceWhitelistUnit] = Field(default_factory=list)
