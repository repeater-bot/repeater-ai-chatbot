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

    linalg_a = np.linalg.norm(a)
    linalg_b = np.linalg.norm(b)

    linalg = linalg_a * linalg_b

    if linalg == 0:
        return float("nan")
    
    cos = np.dot(a, b) / linalg
    return float(cos)