from pydantic import BaseModel

class SimilarityResponse(BaseModel):
    """
    Response model for similarity API
    """
    similarity: float
    first_text: str
    second_text: str