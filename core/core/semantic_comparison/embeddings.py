from ...call_api.embeddings import (
    EmbeddingsRequest,
    EmbeddingsRuntime,
    EmbeddingsResponse,
    Embeddings
)
from .get_model import get_model
from ...runtime_container import RuntimeContainer
from ...global_config_manager import ConfigManager

async def embedding(
    user_id: str,
    input: str | list[str] | list[list[int]],
    model_id: str | list[str] | None = None,
) -> EmbeddingsResponse:
    runtime = RuntimeContainer.get_runtime()
    configs = await runtime.user_config_manager.load(user_id)
    global_configs = ConfigManager.get_configs()
    model_id, model_info = await get_model(
        model_id = model_id,
        model_client = runtime.model_info_client,
        user_configs = configs,
        global_configs = global_configs,
    )

    if not model_info.api_key:
        raise ValueError("API key is required for semantic comparison")

    request = EmbeddingsRequest(
        url = model_info.get_base_url(),
        proxy = model_info.proxy,
        limits = model_info.limits,
        timeout = model_info.timeout,

        key = model_info.api_key,
        model = model_info.id,
        model_id = model_id,
        model_uid = model_info.uid,

        input = input,
    )
    embeddings_runtime = EmbeddingsRuntime(
        client_pool = runtime.openai_pool
    )

    embedding = Embeddings()

    response = await embedding.embeddings(
        request = request,
        runtime = embeddings_runtime,
    )

    return response