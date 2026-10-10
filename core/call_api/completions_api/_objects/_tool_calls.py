from pydantic import BaseModel
from ....user_data_managers.context import (
    CallingRequest,
    SpecifiedFunction,
    ToolTypes
)

class ToolCall(BaseModel):
    """
    Dataclass to store the delta data for a given date.
    """
    id: str = ""
    type: str = ""
    name: str = ""
    arguments: str = ""

    def to_calling_request(self) -> CallingRequest:
        return CallingRequest(
            id = self.id,
            type = ToolTypes(self.type),
            function = SpecifiedFunction(
                name = self.name,
                arguments = self.arguments
            )
        )