import asyncio
from .embeddings import embedding
from .similarities import similarity

async def comparison(
    user_id: str,
    text1: str,
    text2: str,
    model_id: str | list[str] | None = None,
):
    response = await embedding(
        user_id,
        [text1, text2],
        model_id,
    )

    result = await asyncio.to_thread(
        similarity,
        response,
    )

    return result