from pydantic import BaseModel


class SimilarityRequest(BaseModel):
    """
    Request model for similarity API
    """
    first_text: str
    second_text: str
    model: str | None = None