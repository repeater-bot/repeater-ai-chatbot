from pydantic import BaseModel

class DataServerConfig(BaseModel):
    """Data server model"""
    base_url: str = ""
    timeout: int | float | None = None
