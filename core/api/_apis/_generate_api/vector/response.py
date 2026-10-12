from pydantic import BaseModel

class VectorResponse(BaseModel):
    """
    Response model for vector API
    """
    vectors: list[list[float]]