import httpx
import orjson

from urllib.parse import quote
from typing import (
    AsyncGenerator,
    Any,
)
from uuid import UUID

from loguru import logger

from ...http_response import Response
from .responses import *
from .exceptions import *

class NexusClient:
    def __init__(
            self,
            base_url: str,
            request_timeout: int | float | None = 60,
            params: dict[str, str | int | float | bool | None] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            auth: tuple[str, str] | None = None,
            transport: httpx.AsyncHTTPTransport | None = None
        ) -> None:
        self._client = httpx.AsyncClient(
            base_url = base_url,
            timeout = request_timeout,
            params = params,
            headers = headers,
            cookies = cookies,
            auth = auth,
            transport = transport
        )
    
    async def close(self) -> None:
        await self._client.aclose()
    
    def _check_uuid(self, uuid: str) -> UUID:
        try:
            return UUID(uuid)
        except ValueError as e:
            raise InvalidUUIDError(f"{uuid} is not a valid UUID") from e
    
    async def submit(self, pool: str, content: dict[str, Any], timeout: int | None = None) -> Response[SubmitResponse]:
        logger.info(
            "Submitting content to {pool}",
            pool = pool
        )
        response = await self._client.post(
            f"/api/{quote(pool)}/submit",
            json = {
                "content": content,
                "timeout": timeout
            }
        )
        return Response(
            response = response,
            model = SubmitResponse
        )
    
    async def download(self, pool: str, resources_uuid: str, data_id: str) -> Response[DownloadResponse]:
        logger.info(
            "Downloading resources {resources_uuid} from {pool}",
            resources_uuid = resources_uuid,
            pool = pool
        )
        response = await self._client.get(
            f"/api/{quote(pool)}/resources/{self._check_uuid(resources_uuid)}/download/{quote(data_id)}"
        )

        return Response(
            response = response,
            model = DownloadResponse
        )
    
    async def update(self, pool: str, resources_uuid: str, content: dict[str, Any], timeout: int | None = None) -> Response[UpdateResponse]:
        logger.info(
            "Updating resources {resources_uuid} in {pool}",
            resources_uuid = resources_uuid,
            pool = pool
        )
        response = await self._client.put(
            f"/api/{quote(pool)}/resources/{self._check_uuid(resources_uuid)}/update",
            json = {
                "content": content,
                "timeout": timeout
            }
        )
        return Response(
            response = response,
            model = UpdateResponse
        )
    
    async def resources_list(self, pool: str) -> list[str]:
        logger.info(
            "Getting resources list in {pool}",
            pool = pool
        )
        response = await self._client.get(
            f"/api/{quote(pool)}/resources_list"
        )
        data = response.json()
        if not isinstance(data, list):
            raise ResponseTypeError(
                "Invalid response from server"
            )
        return data
    
    async def resources_list_stream(self, pool: str) -> AsyncGenerator[str, None]:
        logger.info(
            "Getting resources list in {pool}",
            pool = pool
        )
        response = await self._client.get(
            f"/api/{quote(pool)}/resources_list/stream"
        )
        async for line in response.aiter_lines():
            try:
                data = orjson.loads(line)
            except orjson.JSONDecodeError:
                logger.warning(
                    "Failed to decode line: {line}",
                    line = line
                )
                continue

            if isinstance(data, str):
                yield data
            else:
                logger.warning(
                    "Invalid data type: {data}(type: {type})",
                    data = data,
                    type = type(data).__name__
                )
    
    async def data_list(self, pool: str, resource: str) -> list[str]:
        logger.info(
            "Getting data list in {pool}/{resource}",
            pool = pool,
            resource = resource
        )
        response = await self._client.get(
            f"/api/{quote(pool)}/data_list/{quote(resource)}"
        )
        data = await response.json()
        if not isinstance(data, list):
            raise TypeError(
                "Invalid response from server"
            )
        return data
    
    async def data_list_stream(self, pool: str, resource: str) -> AsyncGenerator[str, None]:
        logger.info(
            "Getting data list in {pool}/{resource}",
            pool = pool,
            resource = resource
        )
        response = await self._client.get(
            f"/api/{quote(pool)}/data_list/{quote(resource)}"
        )
        async for line in response.aiter_lines():
            data = orjson.loads(line)
            if not isinstance(data, str):
                logger.warning(
                    "Invalid response from server"
                )
                continue
            yield data
    
    async def remove(self, pool: str, resources_uuid: str) -> Response[RemoveResponse]:
        logger.info(
            "Removing resources {resources_uuid} from {pool}",
            resources_uuid = resources_uuid,
            pool = pool
        )
        response = await self._client.delete(
            f"/api/{quote(pool)}/resources/{self._check_uuid(resources_uuid)}/remove/resource"
        )
        return Response(
            response = response,
            model = RemoveResponse
        )
    
    async def remove_data(self, pool: str, resources_uuid: str, data_id: str) -> Response[RemoveResponse]:
        logger.info(
            "Removing resources {resources_uuid} from {pool}",
            resources_uuid = resources_uuid,
            pool = pool
        )
        response = await self._client.delete(
            f"/api/{quote(pool)}/resources/{self._check_uuid(resources_uuid)}/remove/data/{quote(data_id)}"
        )
        return Response(
            response = response,
            model = RemoveResponse
        )