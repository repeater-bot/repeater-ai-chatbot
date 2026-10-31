from __future__ import annotations

import base64
import httpx

from collections.abc import Mapping
from urllib.parse import quote
from ...special_exception import HTTPException
from ._model import (
    CopyRangeResult,
    CopyResult,
    DeleteResult,
    DiskUsage,
    FileInfo,
    HashResult,
    MoveResult,
)


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

        self.client = httpx.AsyncClient(
            base_url = base_url,
            timeout = timeout,
            params = params,
            headers = headers,
            cookies = cookies,
            auth = auth,
            transport = transport
        )

    @property
    def base_url(self) -> httpx.URL:
        return self.client.base_url

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
            *,
            allowed_statuses: tuple[int, ...] = (),
            **kwargs
        ) -> httpx.Response:
        try:
            response = await self.client.request(method, url, **kwargs)
        except httpx.RequestError as e:
            raise HTTPException(detail = f"{action} Data Resource Failed: {e}") from e

        if response.is_error and response.status_code not in allowed_statuses:
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

    async def get_file_response(
        self,
        path: str,
        headers: Mapping[str, str] | None = None
    ) -> httpx.Response:
        """Read a file and return the raw response, preserving range headers.

        A 416 response is returned instead of raised so callers can forward its
        ``Content-Range`` header.
        """
        return await self._request(
            "GET",
            self.operation_url("read", path),
            "Get",
            headers = dict(headers) if headers else None,
            allowed_statuses = (416,)
        )

    async def get_file(
        self,
        path: str,
        start: int | None = None,
        length: int | None = None,
        headers: Mapping[str, str] | None = None
    ) -> bytes:
        """Read a file as raw bytes, optionally a byte range.

        ``start`` is zero-based; ``length=None`` reads to EOF.  A range is sent
        as the standard ``Range`` request header.
        """
        request_headers = dict(headers or {})
        if start is None and length is not None:
            start = 0
        if start is not None:
            if start < 0:
                raise ValueError("start must not be negative")
            if length is not None and length < 0:
                raise ValueError("length must not be negative")
            end = "" if length is None else str(start + length - 1)
            request_headers["Range"] = f"bytes={start}-{end}"

        response = await self.get_file_response(path, request_headers)
        if response.status_code == 416:
            raise HTTPException(
                detail = "Range Not Satisfiable",
                status_code = 416
            )
        return response.content

    async def get_file_url(
        self,
        path: str,
    ) -> httpx.URL:
        """Get a file URL.

        This is useful for downloading files from the server.
        """
        return self.base_url.join(self.operation_url("read", path))
        
    async def get_text(
        self,
        path: str,
        text_encoding: str = "utf-8",
        start: int | None = None,
        length: int | None = None,
        headers: Mapping[str, str] | None = None
    ) -> str:
        """Read a file as text, optionally a byte range."""
        if start is not None:
            if start < 0:
                raise ValueError("start must not be negative")
            if length is not None and length < 0:
                raise ValueError("length must not be negative")

        request_headers = dict(headers or {})
        if start is None and length is not None:
            start = 0
        if start is not None:
            end = "" if length is None else str(start + length - 1)
            request_headers["Range"] = f"bytes={start}-{end}"

        response = await self._request(
            "GET",
            self.operation_url("read", path),
            "Get",
            params = {
                "text_encoding": text_encoding,
            },
            headers = request_headers
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

    async def is_file(self, path: str) -> bool:
        """Return whether a virtual path is a file."""
        response = await self._request(
            "GET",
            self.operation_url("is_file", path),
            "Is File"
        )
        payload = response.json()
        if not isinstance(payload, dict):
            raise HTTPException(
                detail = "Invalid Data Server is_file response",
                status_code = 502
            )
        return bool(payload.get("is_file", False))

    async def is_dir(self, path: str) -> bool:
        """Return whether a virtual path is a directory."""
        response = await self._request(
            "GET",
            self.operation_url("is_dir", path),
            "Is Dir"
        )
        payload = response.json()
        if not isinstance(payload, dict):
            raise HTTPException(
                detail = "Invalid Data Server is_dir response",
                status_code = 502
            )
        return bool(payload.get("is_dir", False))

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

    @staticmethod
    def _size_result(response: httpx.Response, action: str) -> int:
        """Read the ``{"size": int}`` payload of a Data Server mutation."""
        try:
            payload = response.json()
        except ValueError as e:
            raise HTTPException(
                detail = f"Invalid Data Server {action} response",
                status_code = 502
            ) from e

        size = payload.get("size") if isinstance(payload, dict) else payload
        if isinstance(size, bool) or not isinstance(size, int):
            raise HTTPException(
                detail = f"Invalid Data Server {action} response",
                status_code = 502
            )
        return size

    async def append(self, path: str, data: bytes) -> int:
        """Append raw bytes to ``path``, creating the file when missing."""
        if not path.strip("/"):
            raise ValueError("path cannot be empty")

        response = await self._request(
            "POST",
            self.operation_url("append", path),
            "Append",
            content = data,
            headers = {
                "Content-Type": "application/octet-stream",
            }
        )
        return self._size_result(response, "append")

    async def truncate(self, path: str, size: int) -> int:
        """Truncate or extend ``path`` to exactly ``size`` bytes."""
        if not path.strip("/"):
            raise ValueError("path cannot be empty")
        if size < 0:
            raise ValueError("size must not be negative")

        response = await self._request(
            "POST",
            self.operation_url("truncate", path),
            "Truncate",
            params = {
                "size": size,
            }
        )
        return self._size_result(response, "truncate")

    async def touch(self, path: str) -> int:
        """Create ``path`` when missing and update its modification time."""
        if not path.strip("/"):
            raise ValueError("path cannot be empty")

        response = await self._request(
            "POST",
            self.operation_url("touch", path),
            "Touch"
        )
        return self._size_result(response, "touch")

    async def edit(
            self,
            path: str,
            data: bytes,
            start: int,
            end: int
        ) -> int:
        """Replace the ``[start, end)`` byte range of ``path`` with ``data``."""
        if not path.strip("/"):
            raise ValueError("path cannot be empty")
        if start < 0:
            raise ValueError("start must not be negative")
        if end < 0:
            raise ValueError("end must not be negative")
        if end < start:
            raise ValueError("end must not be less than start")

        response = await self._request(
            "POST",
            self.operation_url("edit", path),
            "Edit",
            json = {
                "start": start,
                "end": end,
                "data": base64.b64encode(data).decode("ascii"),
            }
        )
        return self._size_result(response, "edit")

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

    async def mkdir(self, path: str) -> str:
        """Create a directory, including missing parents."""
        if not path.strip("/"):
            raise ValueError("path cannot be empty")

        response = await self._request(
            "POST",
            self.operation_url("mkdir", path),
            "Mkdir"
        )
        payload = response.json()
        if not isinstance(payload, dict) or "path" not in payload:
            raise HTTPException(
                detail = "Invalid Data Server mkdir response",
                status_code = 502
            )
        return str(payload["path"])

    async def move(self, path: str, destination: str) -> MoveResult:
        """Move a file or directory without changing file ids or payloads."""
        response = await self._request(
            "POST",
            self.operation_url("move", path),
            "Move",
            json = {
                "destination": destination,
            }
        )
        return MoveResult.model_validate(response.json())

    async def copy(self, path: str, destination: str) -> CopyResult:
        """Copy a file or directory with fresh file ids and payloads."""
        response = await self._request(
            "POST",
            self.operation_url("copy", path),
            "Copy",
            json = {
                "destination": destination,
            }
        )
        return CopyResult.model_validate(response.json())

    async def hash(self, path: str, algorithm: str = "sha256") -> HashResult:
        """Compute the digest of a file with ``algorithm``."""
        response = await self._request(
            "GET",
            self.operation_url("hash", path),
            "Hash",
            params = {
                "algorithm": algorithm,
            }
        )
        return HashResult.model_validate(response.json())

    async def du(self, path: str) -> DiskUsage:
        """Measure the total size and the entry counts below ``path``."""
        response = await self._request(
            "GET",
            self.operation_url("du", path),
            "Disk Usage"
        )
        return DiskUsage.model_validate(response.json())

    async def tree(self, path: str, max_depth: int = -1) -> dict:
        """Return the nested node tree below ``path``.

        ``max_depth=-1`` walks the whole subtree.
        """
        response = await self._request(
            "GET",
            self.operation_url("tree", path),
            "Tree",
            params = {
                "max_depth": max_depth,
            }
        )
        payload = response.json()
        if not isinstance(payload, dict):
            raise HTTPException(
                detail = "Invalid Data Server tree response",
                status_code = 502
            )
        return payload

    async def copy_range(
            self,
            path: str,
            destination: str,
            start: int,
            end: int
        ) -> CopyRangeResult:
        """Copy the ``[start, end)`` byte range of ``path`` to ``destination``."""
        if not path.strip("/"):
            raise ValueError("path cannot be empty")
        if start < 0:
            raise ValueError("start must not be negative")
        if end < 0:
            raise ValueError("end must not be negative")
        if end < start:
            raise ValueError("end must not be less than start")

        response = await self._request(
            "POST",
            self.operation_url("copy_range", path),
            "Copy Range",
            json = {
                "destination": destination,
                "start": start,
                "end": end,
            }
        )
        return CopyRangeResult.model_validate(response.json())

    async def close(self) -> None:
        await self.client.aclose()
