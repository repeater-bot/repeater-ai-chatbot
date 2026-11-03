from pydantic import BaseModel, Field
from .writelist_unit import RealspaceWritelistUnit

class RealspaceConfigs(BaseModel):
    writelist: list[RealspaceWritelistUnit] = Field(default_factory=list)
