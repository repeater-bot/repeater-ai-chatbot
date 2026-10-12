from pydantic import BaseModel


class VectorRequest(BaseModel):
    """
    Request model for vector API
    """
    texts: list[str]
    model: str | None = None