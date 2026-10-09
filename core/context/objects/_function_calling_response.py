from pydantic import BaseModel, Field
from ._tool_types import ToolTypes

class SpecifiedFunction(BaseModel):
    name: str = ""
    arguments: str = ""

class CallingRequest(BaseModel):
    id: str
    type: ToolTypes = ToolTypes.FUNCTION
    function: SpecifiedFunction = Field(default_factory = SpecifiedFunction)