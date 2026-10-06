from pydantic import BaseModel

class WatermarkRequest(BaseModel):
    text: str
    image: str
    output_format: str = ".png"