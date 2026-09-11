from pydantic import BaseModel, Field
from typing import Any
from ....auxiliary.http import (
    ClientLimits,
    ClientTimeout
)
from .encoding_format import EncodingFormat

class EmbeddingsRequest(BaseModel):
    url: str = ""
    proxy: str | None = None
    limits: ClientLimits = Field(default_factory=ClientLimits)
    encoding: str = "utf-8"
    headers: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    cookies: dict[str, Any] = Field(default_factory=dict)
    timeout: int | float | ClientTimeout = 600.0

    model: str = ""
    model_id: str | list[str] = ""
    model_uid: str = ""
    key: str = ""

    input: str | list[str] | list[list[int]] = Field(...)
    dimensions: int | None = Field(default=None)
    encoding_format: EncodingFormat | None = Field(default=None)
    user: str | None = Field(default=None)