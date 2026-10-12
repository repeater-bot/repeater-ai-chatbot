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
    id: str | None = None
    type: str | None = None
    name: str | None = None
    arguments: str | None = None
    index: int | None = None

    def to_calling_request(self) -> CallingRequest:
        # index 只用于流式累积时归并，不属于 CallingRequest 契约，故不检查
        if self.id is None or self.type is None or self.name is None or self.arguments is None:
            raise ValueError("ToolCall is missing required fields")
        
        return CallingRequest(
            id = self.id,
            type = ToolTypes(self.type),
            function = SpecifiedFunction(
                name = self.name,
                arguments = self.arguments
            )
        )