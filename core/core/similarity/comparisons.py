import json
import asyncio
from .embeddings import embedding
from .similarities import similarity
from loguru import logger

async def comparison(
    user_id: str,
    first_text: str,
    second_text: str,
    model_id: str | list[str] | None = None,
):
    response = await embedding(
        user_id,
        [first_text, second_text],
        model_id,
    )

    result = await asyncio.to_thread(
        similarity,
        response,
    )

    logger.info(
        "Similarity: \nFirst Text: {text1}\nSecond Text: {text2}\nResult: {result}\nPrompt Tokens: {prompt_usage}\nToken Tokens: {token_usage}",
        text1 = json.dumps(first_text, ensure_ascii = False),
        text2 = json.dumps(second_text, ensure_ascii = False),
        prompt_usage = response.prompt_tokens,
        token_usage = response.total_tokens,
        result = result,
    )

    return result