from .request import SimilarityRequest
from .response import SimilarityResponse
from .._router import generate_router
from .....core.similarity import comparison

@generate_router.post("/similarity/{user_id}")
async def similarity(request: SimilarityRequest, user_id: str):
    """
    Similarity API

    Calculate the similarity of two texts.
    """
    similarity = await comparison(
        user_id = user_id,
        first_text = request.first_text,
        second_text = request.second_text,
        model_id = request.model
    )
    return SimilarityResponse(
        similarity = similarity,
        first_text = request.first_text,
        second_text = request.second_text
    )