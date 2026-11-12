from __future__ import annotations

from typing import Any

import httpx

from .....global_config_manager import ConfigManager
from .....special_exception import HTTPException


class SQLiteProxy:
    """Backend-side proxy for the SQLite API owned by DataServer."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            config = ConfigManager.get_configs().data_server
            self._client = httpx.AsyncClient(
                base_url = config.base_url.rstrip("/"),
                timeout = config.timeout,
            )
        return self._client

    async def _request(
        self,
        method: str,
        url: str,
        action: str,
        **kwargs
    ) -> dict[str, Any]:
        try:
            response = await self.client.request(method, url, **kwargs)
        except httpx.HTTPError as error:
            raise HTTPException(
                detail = f"DataServer SQLite {action} failed: {error}",
                status_code = 502
            ) from error
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            raise HTTPException(detail=detail, status_code=response.status_code)
        try:
            return response.json()
        except ValueError as error:
            raise HTTPException(
                detail = f"Invalid DataServer SQLite {action} response",
                status_code = 502
            ) from error

    async def create(self, path: str) -> tuple[str, str]:
        data = await self._request(
            "POST", "/sqlite/create", "create", json = {"path": path}
        )
        return data["id"], data["path"]

    async def open(self, path: str) -> tuple[str, str]:
        data = await self._request(
            "POST", "/sqlite/open", "open", json = {"path": path}
        )
        return data["id"], data["path"]

    async def list_open(self) -> list[dict[str, str]]:
        return await self._request("GET", "/sqlite/list", "list")

    async def execute(
        self,
        session_id: str,
        sql: str,
        params: list[Any] | dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/sqlite/{session_id}/execute",
            "execute",
            json = {
                "sql": sql,
                "params": params,
            }
        )

    async def close(self, session_id: str) -> None:
        await self._request("DELETE", f"/sqlite/{session_id}", "close")


sqlite_manager = SQLiteProxy()
