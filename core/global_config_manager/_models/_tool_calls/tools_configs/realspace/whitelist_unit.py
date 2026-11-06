from pydantic import BaseModel
from .shell_level import ShellLevel

class RealspaceWhitelistUnit(BaseModel):
    path: str
    read: bool = False
    write: bool = False
    shell_level: ShellLevel = ShellLevel.OFF
