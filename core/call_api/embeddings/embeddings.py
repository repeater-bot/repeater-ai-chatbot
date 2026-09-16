import httpx
from openai import AsyncOpenAI
from openai.types.create_embedding_response import CreateEmbeddingResponse
from ...pools.client_pool import ClientInfo
from .objects import (
    EmbeddingsRequest,
    EmbeddingsResponse,
    EmbeddingsRuntime,
    EmbeddingsData
)
from ..assists import none_to_omit

class Embeddings:
    
    @staticmethod
    def _get_client(request: EmbeddingsRequest, runtime: EmbeddingsRuntime) -> tuple[AsyncOpenAI, httpx.AsyncClient]:
        client_info = ClientInfo(
            url = request.url,
            proxy = request.proxy,
            limits = request.limits,
            timeout = request.timeout,
            encoding = request.encoding,
        )
        openai, client = runtime.client_pool.get_openai_and_client(
            client_info = client_info,
            api_key = request.key,
            params = request.params,
            headers = request.headers,
            cookies = request.cookies,
        )
        return openai, client

    def translation_response(self, response: CreateEmbeddingResponse) -> EmbeddingsResponse:
        embeddings: list[EmbeddingsData] = []
        for data in response.data:
            embeddings.append(
                EmbeddingsData(
                    index = data.index,
                    object = data.object,
                    embedding = data.embedding,
                )
            )
        return EmbeddingsResponse(
            model = response.model,
            datas = embeddings,
            prompt_tokens = response.usage.prompt_tokens,
            total_tokens = response.usage.total_tokens,
        )

    async def embeddings(self, request: EmbeddingsRequest, runtime: EmbeddingsRuntime) -> EmbeddingsResponse:
        openai, client = self._get_client(request, runtime)

        response = await openai.embeddings.create(
            input = request.input,
            model = request.model,
            dimensions = none_to_omit(request.dimensions),
            encoding_format = none_to_omit(request.encoding_format, lambda x: x.value)
        )

        return self.translation_response(response)