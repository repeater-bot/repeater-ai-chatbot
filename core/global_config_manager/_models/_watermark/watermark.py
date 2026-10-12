from pydantic import BaseModel
from .correction_level import WatermarkCorrectionLevel

class WatermarkConfig(BaseModel):

    base_url: str = ""
    timeout: int = 60
    block_size: int = 4
    correction_level: WatermarkCorrectionLevel | float = WatermarkCorrectionLevel.MEDIUM
    base_size: int = 128
    size_header_width: int = 8
    default_image_watermark: str = "Repeater Image Watermark"