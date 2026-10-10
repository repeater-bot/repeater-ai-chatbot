from pydantic import BaseModel
from ...context import ToolTypes
from typing import Any

class FunctionStruct(BaseModel):
    description: str = ""
    name: str = ""
    parameters: dict[str, Any] | None = None
    strict: bool = False

class ToolStruct(BaseModel):
    type: ToolTypes = ToolTypes.FUNCTION
    function: FunctionStruct