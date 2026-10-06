from .request import VectorRequest
from .response import VectorResponse
from .._router import generate_router
from .....core.vectors import vectors

@generate_router.post("/vector/{user_id}")
async def vectors_endpoint(request: VectorRequest, user_id: str):
    """
    Vectors API

    Calculate the vectors of the texts.
    """
    vectors_result = await vectors(
        user_id = user_id,
        texts = request.texts,
        model_id = request.model
    )
    return VectorResponse(
        vectors = vectors_result
    )