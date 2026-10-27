from __future__ import annotations

import httpx

from urllib.parse import quote
from yarl import URL
from ...special_exception import HTTPException
from ._model import DeleteResult, FileInfo


class DataClient:
    """Async client for the Workspace Data Server.

    The server exposes ``read`` / ``write`` / ``list`` / ``info`` under
    ``/operations``; paths are virtual paths relative to its ``base_path``.
    """

    def __init__(
            self,
            base_url: str,
            timeout: int | float | None = None,
            params: dict[str, str | int | float | bool | None] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            auth: tuple[str, str] | None = None,
            transport: httpx.AsyncHTTPTransport | None = None,
        ):
        if isinstance(base_url, str):
            if base_url:
                self._base_url = URL(base_url)
            else:
                raise ValueError("base_url cannot be empty")
        else:
            raise TypeError("base_url must be a string")

        self.client = httpx.AsyncClient(
            base_url = str(self._base_url),
            timeout = timeout,
            params = params,
            headers = headers,
            cookies = cookies,
            auth = auth,
            transport = transport
        )

    @property
    def base_url(self) -> URL:
        return self._base_url

    @staticmethod
    def quote_path(path: str) -> str:
        """Normalise a virtual path and percent-encode it for a URL."""
        if not isinstance(path, str):
            raise TypeError("path must be a string")
        return quote(path.lstrip("/"))

    def operation_url(self, operation: str, path: str = "") -> str:
        """Build the URL of a Data Server operation."""
        return f"/operations/{operation}/{self.quote_path(path)}"

    async def _request(
            self,
            method: str,
            url: str,
            action: str,
            **kwargs
        ) -> httpx.Response:
        try:
            response = await self.client.request(method, url, **kwargs)
        except httpx.RequestError as e:
            raise HTTPException(detail = f"{action} Data Resource Failed: {e}") from e

        if response.is_error:
            try:
                payload = response.json()
            except ValueError:
                detail = response.text
            else:
                if isinstance(payload, dict):
                    detail = payload.get("detail", response.text)
                else:
                    detail = response.text

            raise HTTPException(
                detail = str(detail) if detail else response.reason_phrase,
                status_code = response.status_code
            )

        return response

    async def get_file(self, path: str) -> bytes:
        """Read a file as raw bytes."""
        response = await self._request(
            "GET",
            self.operation_url("read", path),
            "Get"
        )
        return response.content

    async def get_text(self, path: str, text_encoding: str = "utf-8") -> str:
        """Read a file as text."""
        response = await self._request(
            "GET",
            self.operation_url("read", path),
            "Get",
            params = {
                "text_encoding": text_encoding,
            }
        )
        return response.text

    async def list_dir(
        self,
        path: str = "",
        recursive: bool = False
    ) -> list[str]:
        """List child paths; ``recursive=True`` returns all descendants."""
        response = await self._request(
            "GET",
            self.operation_url("list", path),
            "List",
            params = {
                "recursive": recursive,
            }
        )
        return self._path_list(response)

    @staticmethod
    def _path_list(response: httpx.Response) -> list[str]:
        payload = response.json()
        if not isinstance(payload, list):
            raise HTTPException(
                detail = "Invalid Data Server path list response",
                status_code = 502
            )
        return [str(item) for item in payload]

    async def glob(
        self,
        path: str,
        pattern: str,
        recursive: bool = False
    ) -> list[str]:
        """Match ``pattern`` below ``path``, returning full virtual paths.

        With ``recursive=True`` the pattern is applied at any depth.
        """
        response = await self._request(
            "GET",
            self.operation_url("glob", path),
            "Glob",
            params = {
                "pattern": pattern,
                "recursive": recursive,
            }
        )
        return self._path_list(response)

    async def rematch(self, path: str, pattern: str) -> bool:
        """Return whether ``path`` matches the regular expression ``pattern``."""
        response = await self._request(
            "GET",
            self.operation_url("rematch", path),
            "Rematch",
            params = {
                "pattern": pattern,
            }
        )
        payload = response.json()
        if not isinstance(payload, dict):
            raise HTTPException(
                detail = "Invalid Data Server rematch response",
                status_code = 502
            )
        return bool(payload.get("matched", False))

    async def get_info(self, path: str) -> FileInfo:
        """Fetch file metadata."""
        response = await self._request(
            "GET",
            self.operation_url("info", path),
            "Get Info"
        )
        return FileInfo.model_validate(response.json())

    async def exists(self, path: str) -> bool:
        """Return whether a virtual path exists."""
        response = await self._request(
            "GET",
            self.operation_url("exists", path),
            "Check"
        )
        payload = response.json()
        if not isinstance(payload, dict):
            raise HTTPException(
                detail = "Invalid Data Server exists response",
                status_code = 502
            )
        return bool(payload.get("exists", False))

    async def write_file(
            self,
            path: str,
            data: bytes,
            filename: str | None = None,
            content_type: str = "application/octet-stream"
        ) -> int:
        """Write bytes to ``path``; the server creates missing nodes."""
        if not path.strip("/"):
            raise ValueError("path cannot be empty")

        files = {
            "file": (
                filename or path.rstrip("/").rsplit("/", 1)[-1],
                data,
                content_type
            )
        }
        response = await self._request(
            "POST",
            self.operation_url("write", path),
            "Write",
            files = files
        )
        try:
            return int(response.text)
        except ValueError as e:
            raise HTTPException(
                detail = "Invalid Data Server write response",
                status_code = 502
            ) from e

    async def delete(self, path: str, recursive: bool = False) -> DeleteResult:
        """Delete a file or directory.

        A non-empty directory requires ``recursive=True``.  The root
        directory cannot be deleted.
        """
        if not path.strip("/"):
            raise ValueError("path cannot be empty")

        response = await self._request(
            "DELETE",
            self.operation_url("delete", path),
            "Delete",
            params = {
                "recursive": recursive,
            }
        )
        return DeleteResult.model_validate(response.json())

    async def close(self) -> None:
        await self.client.aclose()
