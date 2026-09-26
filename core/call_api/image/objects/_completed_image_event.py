from pydantic import BaseModel, ConfigDict
from .auxiliary.stream_usage import StreamUsage
from typing import Literal

class CompletedImageEvent(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    b64_json: str | None = None
    background: str | None = None
    created_at: int | None = None
    output_format: str | None = None
    partial_image_index: int | None = None
    quality: str | None = None
    size: str | None = None
    type: Literal["image_generation.completed"] = "image_generation.completed"
    usage: StreamUsage | None = None