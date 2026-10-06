from pydantic import BaseModel
from typing import Literal

class WatermarkConfig(BaseModel):

    base_url: str = ""
    timeout: int = 60
    base_size: int = 512
    size_header_width: int = 8
    default_image_watermark: str = "Repeater Image Watermark"