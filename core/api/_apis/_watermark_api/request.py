from pydantic import BaseModel

class WatermarkRequest(BaseModel):
    image: str
    text: str | None = None
    output_format: str = ".png"