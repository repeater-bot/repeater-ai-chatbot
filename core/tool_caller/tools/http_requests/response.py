from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class Response(BaseModel):
    request_id: str = Field(..., description="The ID of the request that generated this response.")
    status_code: int | None = Field(default=None, description="The HTTP status code of the response.")
    response_time: datetime = Field(default_factory=datetime.now, description="The time when the response was received.")
    reason: str = Field(default="", description="The reason for the response.")
    headers: dict | None = Field(default=None, description="HTTP headers from the response.")
    cookies: dict | None = Field(default=None, description="Cookies from the response.")
    data: Any = Field(default=None, description="The data returned by the response.")
