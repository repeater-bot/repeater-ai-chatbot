from ..similarity import embedding

async def vectors(
    user_id: str,
    texts: list[str],
    model_id: str | list[str] | None = None,
):
    response = await embedding(
        user_id = user_id,
        input = texts,
        model_id = model_id,
    )

    return [
        data.embedding
        for data in response.datas
    ]