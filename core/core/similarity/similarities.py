import numpy as np
from ...call_api.embeddings import (
    EmbeddingsResponse,
)

def similarity(
    response: EmbeddingsResponse
) -> float:
    if len(response.datas) != 2:
        raise ValueError("EmbeddingsResponse must have two datas")

    a = response.datas[0].to_numpy()
    b = response.datas[1].to_numpy()

    cos = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    return float(cos)