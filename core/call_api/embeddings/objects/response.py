import numpy as np
from pydantic import BaseModel, Field
from typing import Literal, TypeVar

T = TypeVar("T", bound=np.typing.DTypeLike)

class EmbeddingsData(BaseModel):
    """
    EmbeddingsData class for handling embeddings data from API.
    """
    embedding: list[float] = Field(default_factory=list)

    index: int = 0

    object: Literal["embedding"] = "embedding"

    def to_numpy(self, dtype: T = np.float64) -> np.ndarray[tuple[int], np.dtype[T]]: # type: ignore
        """
        Convert the embedding data to a numpy array.

        Returns:
            np.ndarray: The embedding data as a numpy array.
        """
        return np.array(self.embedding, dtype = dtype)

class EmbeddingsResponse(BaseModel):
    """
    EmbeddingResponse class for handling embedding response from API.
    """
    datas: list[EmbeddingsData] = Field(default_factory=list)

    model: str = ""

    prompt_tokens: int = 0
    total_tokens: int = 0