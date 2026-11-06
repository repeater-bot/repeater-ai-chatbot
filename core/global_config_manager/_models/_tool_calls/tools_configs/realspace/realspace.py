from pydantic import BaseModel, Field
from .whitelist_unit import RealspaceWhitelistUnit

class RealspaceConfigs(BaseModel):
    whitelist: dict[str, RealspaceWhitelistUnit] = Field(default_factory=dict)
