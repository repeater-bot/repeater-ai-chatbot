import ssl
import httpx
import random

from urllib.parse import quote
from .responses import (
    ModelInfoResponse,
    DisableResponse,
    RefreshResponse
)
from ...global_config_manager import ConfigManager
from ._models import ModelInfo
from ...special_exception import HTTPException
from ...http_response import Response

class ModelsClient:
    def __init__(
            self,
            base_url: str,
            api_key: str | None = None,
            timeout: int | float | None = None,
            params: dict[str, str | int | float | bool | None] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            auth: tuple[str, str] | None = None,
            verify: ssl.SSLContext | str | bool = True,
            transport: httpx.AsyncHTTPTransport | None = None,
        ):
        self._base_url = base_url
        if headers is None:
            headers = {}
        headers.update({
            "Authorization": f"Bearer {api_key}"
        })
        self._client = httpx.AsyncClient(
            base_url = self._base_url,
            timeout = timeout,
            params = params,
            headers = headers,
            cookies = cookies,
            auth = auth,
            verify = verify,
            transport = transport
        )
    
    async def get_model_list(
        self,
        model_id: str | list[str] | None,
    ) -> list[ModelInfo]:
        if model_id is None:
            raise HTTPException(
                status_code = 400,
                detail = "Model ID is required"
            )
        
        if isinstance(model_id, str):
            model_id = [model_id]
        
        models: list[ModelInfo] = []
        for id in model_id:
            # 获取API信息
            response = await self.get_models(id)
            if response.code != 200:
                raise HTTPException(
                    status_code = response.code,
                    detail = f"Model Info Server Error: {response.text}",
                )
            model_info = response.get_data()
            if model_info is None:
                raise HTTPException(
                    status_code = 404,
                    detail = "Error: Response is invalid."
                )
            models.extend(model_info.models)
            if model_info.models:
                break
        
        if models is None:
            raise HTTPException(
                status_code = 404,
                detail = "Error: Model Info Server Response is Empty.",
            )
        
        models = model_info.models
        if not models:
            raise HTTPException(
                status_code = 404,
                detail = "Error: Model is Not Found.",
            )
        
        return models
        
    async def get_random_model(self, model_id: str | list[str]) -> ModelInfo:
        random_decay_index = ConfigManager.get_configs().model_api.random_decay_index
        models = await self.get_model_list(model_id)
        if len(models) == 1:
            return models[0]
        choice_models = random.choices(models, weights = [random_decay_index ** index for index in range(len(models))], k=1)

        return choice_models[0]
    
    async def get_models(self, model_id: str) -> Response[ModelInfoResponse]:
        try:
            http_response = await self._client.get(
                f"/models/{quote(model_id)}"
            )
        except httpx.RequestError as e:
            raise HTTPException(detail = f"Get Models API Failed: {e}") from e
        
        response = Response(
            response = http_response,
            model = ModelInfoResponse
        )

        return response
    
    async def get_all_models(self) -> Response[ModelInfoResponse]:
        try:
            http_response = await self._client.get(
                "/models"
            )
        except httpx.RequestError as e:
            raise HTTPException(detail = f"Get All Models API Failed: {e}") from e

        response = Response(
            response = http_response,
            model = ModelInfoResponse
        )

        return response
    
    async def disable(self, model_id: str, timeout: int) -> Response[DisableResponse]:
        try:
            http_response = await self._client.post(
                f"/disable/{quote(model_id)}",
                json = {
                    "timeout": timeout
                }
            )
        except httpx.RequestError as e:
            raise HTTPException(detail = f"Disable Model API Failed: {e}") from e

        response = Response(
            response = http_response,
            model = DisableResponse
        )

        return response

    async def refresh(self, provider_id: str | None = None) -> Response[RefreshResponse]:
        url = "/refresh"
        if provider_id:
            url += f"/{quote(provider_id)}"

        try:
            http_response = await self._client.post(url)
        except httpx.RequestError as e:
            raise HTTPException(detail = f"Refresh Model Info API Failed: {e}") from e

        response = Response(
            response = http_response,
            model = RefreshResponse
        )
        
        return response