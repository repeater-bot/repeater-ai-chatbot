from __future__ import annotations

import base64
import re
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
    SQLiteAccess,
    SQLiteDatabaseInfo,
    SQLiteExecuteResult,
    TextEditResult,
    TextFile,
    TextLine,
    TextMetadata,
    TextRegexEditResult,
    TextRegexMatch,
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

    async def get_text_file(
        self,
        path: str,
        text_encoding: str = "utf-8"
    ) -> TextFile:
        """Read a whole text file, split it client-side and attach metadata.

        Line numbers are 1-based; character offsets count decoded Unicode code
        points.  No server-side text/line API is used.
        """
        data = await self.get_file(path)
        text = data.decode(text_encoding)
        info = await self.get_info(path)

        lines: list[TextLine] = []
        offset = 0
        raw_lines = text.splitlines(keepends = True) or [""]
        for number, raw_line in enumerate(raw_lines, start = 1):
            if raw_line.endswith("\r\n"):
                content, ending = raw_line[:-2], "\r\n"
            elif raw_line.endswith("\n") or raw_line.endswith("\r"):
                content, ending = raw_line[:-1], raw_line[-1]
            else:
                content, ending = raw_line, ""

            start = offset
            end = start + len(content)
            offset += len(raw_line)
            lines.append(
                TextLine(
                    number = number,
                    start = start,
                    end = end,
                    raw_end = offset,
                    text = content,
                    ending = ending
                )
            )

        if "\r\n" in text:
            newline = "\r\n"
        elif "\n" in text:
            newline = "\n"
        elif "\r" in text:
            newline = "\r"
        else:
            newline = ""

        numbered_content = "".join(
            f"{line.number:>4} | {line.text}{line.ending}"
            for line in lines
        )
        metadata = TextMetadata(
            path = path,
            encoding = text_encoding,
            byte_size = len(data),
            char_count = len(text),
            line_count = len(lines),
            newline = newline,
            st_mtime = info.st_mtime,
            st_mode = info.st_mode
        )
        return TextFile(
            content = text,
            numbered_content = numbered_content,
            lines = lines,
            metadata = metadata
        )

    @staticmethod
    def _text_offset(
        text: str,
        lines: list[TextLine],
        line: int,
        column: int
    ) -> int:
        """Map a 1-based line/column to a character offset.

        ``column == line length + 1`` addresses the position just before the
        line ending; ``line == line_count + 1, column == 1`` addresses EOF.
        """
        if line == len(lines) + 1 and column == 1:
            return len(text)
        if line < 1 or line > len(lines):
            raise ValueError(f"line must be between 1 and {len(lines)}")
        target = lines[line - 1]
        max_column = target.end - target.start + 1
        if column < 1 or column > max_column:
            raise ValueError(
                f"column must be between 1 and {max_column} for line {line}"
            )
        return target.start + column - 1

    @staticmethod
    def _line_column(
        text: str,
        lines: list[TextLine],
        offset: int
    ) -> tuple[int, int]:
        """Map a character offset back to a 1-based line/column."""
        if offset == len(text):
            if lines and not text.endswith(("\n", "\r")):
                last = lines[-1]
                return last.number, last.end - last.start + 1
            return len(lines) + 1, 1
        for line in lines:
            if line.start <= offset <= line.end:
                return line.number, offset - line.start + 1
            if line.start <= offset < line.raw_end:
                return line.number, offset - line.start + 1
        raise ValueError(f"offset {offset} is outside the text")

    async def _commit_text_edit(
        self,
        path: str,
        text_file: TextFile,
        replacement: str,
        start: int,
        end: int,
        mode: str,
        text_encoding: str
    ) -> TextEditResult:
        if start < 0 or end < start or end > len(text_file.content):
            raise ValueError("invalid character range")

        new_text = text_file.content[:start] + replacement + text_file.content[end:]
        data = new_text.encode(text_encoding)
        await self.write_file(path, data)
        info = await self.get_info(path)

        start_line, start_column = self._line_column(
            text_file.content, text_file.lines, start
        )
        end_line, end_column = self._line_column(
            text_file.content, text_file.lines, end
        )
        new_lines = new_text.splitlines(keepends = True) or [""]
        if "\r\n" in new_text:
            newline = "\r\n"
        elif "\n" in new_text:
            newline = "\n"
        elif "\r" in new_text:
            newline = "\r"
        else:
            newline = ""

        metadata = TextMetadata(
            path = path,
            encoding = text_encoding,
            byte_size = len(data),
            char_count = len(new_text),
            line_count = len(new_lines),
            newline = newline,
            st_mtime = info.st_mtime,
            st_mode = info.st_mode
        )
        return TextEditResult(
            path = path,
            mode = mode,
            start_char = start,
            end_char = end,
            start_line = start_line,
            start_column = start_column,
            end_line = end_line,
            end_column = end_column,
            replaced_chars = end - start,
            char_count = len(new_text),
            line_count = len(new_lines),
            size = len(data),
            metadata = metadata
        )

    async def edit_text_by_char(
        self,
        path: str,
        replacement: str,
        start: int,
        end: int | None = None,
        text_encoding: str = "utf-8"
    ) -> TextEditResult:
        """Replace ``[start, end)`` absolute character offsets (0-based)."""
        end = start if end is None else end
        text_file = await self.get_text_file(path, text_encoding)
        return await self._commit_text_edit(
            path, text_file, replacement, start, end, "char", text_encoding
        )

    async def edit_text_by_line(
        self,
        path: str,
        replacement: str,
        start_line: int = 1,
        start_column: int = 1,
        end_line: int | None = None,
        end_column: int | None = None,
        text_encoding: str = "utf-8"
    ) -> TextEditResult:
        """Replace a 1-based line/column range ``[start, end)``."""
        end_line = start_line if end_line is None else end_line
        end_column = start_column if end_column is None else end_column
        text_file = await self.get_text_file(path, text_encoding)
        start = self._text_offset(
            text_file.content, text_file.lines, start_line, start_column
        )
        end = self._text_offset(
            text_file.content, text_file.lines, end_line, end_column
        )
        return await self._commit_text_edit(
            path, text_file, replacement, start, end, "line", text_encoding
        )

    async def edit_text(
        self,
        path: str,
        replacement: str,
        start_char: int | None = None,
        end_char: int | None = None,
        start_line: int | None = None,
        start_column: int = 1,
        end_line: int | None = None,
        end_column: int | None = None,
        text_encoding: str = "utf-8"
    ) -> TextEditResult:
        """Edit using character offsets, line/column, or both.

        If both are supplied they must resolve to the same start/end offsets.
        """
        if start_char is None and start_line is None:
            raise ValueError("start_char or start_line is required")

        text_file = await self.get_text_file(path, text_encoding)
        both = start_char is not None and start_line is not None

        if start_char is not None:
            char_start = start_char
            char_end = start_char if end_char is None else end_char
        else:
            char_start = char_end = None

        if start_line is not None:
            end_line = start_line if end_line is None else end_line
            end_column = start_column if end_column is None else end_column
            line_start = self._text_offset(
                text_file.content, text_file.lines, start_line, start_column
            )
            line_end = self._text_offset(
                text_file.content, text_file.lines, end_line, end_column
            )
        else:
            line_start = line_end = None

        if both:
            if char_start != line_start or char_end != line_end:
                raise ValueError(
                    "character and line/column positions do not match"
                )
            start, end = char_start, char_end
            mode = "both"
        elif char_start is not None:
            start, end = char_start, char_end
            mode = "char"
        else:
            start, end = line_start, line_end
            mode = "line"

        return await self._commit_text_edit(
            path, text_file, replacement, start, end, mode, text_encoding
        )

    async def insert_text(
        self,
        path: str,
        text: str,
        line: int = 1,
        column: int = 1,
        text_encoding: str = "utf-8"
    ) -> TextEditResult:
        """Insert text at a line/column position."""
        return await self.edit_text_by_line(
            path, text, line, column, line, column, text_encoding
        )

    async def insert_text_by_char(
        self,
        path: str,
        text: str,
        char: int,
        text_encoding: str = "utf-8"
    ) -> TextEditResult:
        """Insert text at an absolute character offset."""
        return await self.edit_text_by_char(
            path, text, char, char, text_encoding
        )

    async def delete_text(
        self,
        path: str,
        start_line: int,
        start_column: int,
        end_line: int,
        end_column: int,
        text_encoding: str = "utf-8"
    ) -> TextEditResult:
        """Delete a line/column range."""
        return await self.edit_text_by_line(
            path, "", start_line, start_column, end_line, end_column, text_encoding
        )

    async def delete_text_by_char(
        self,
        path: str,
        start: int,
        end: int,
        text_encoding: str = "utf-8"
    ) -> TextEditResult:
        """Delete an absolute character range."""
        return await self.edit_text_by_char(
            path, "", start, end, text_encoding
        )

    async def edit_text_regex(
        self,
        path: str,
        pattern: str,
        replacement: str,
        count: int = 1,
        ignore_case: bool = False,
        multiline: bool = False,
        dotall: bool = False,
        text_encoding: str = "utf-8"
    ) -> TextRegexEditResult:
        """Regex-scan the whole text, then replace and write it back.

        ``count=0`` replaces every match; ``count=1`` only the first.  The
        replacement string follows ``re.sub`` syntax, so ``\\1`` backreferences
        are supported.
        """
        if count < 0:
            raise ValueError("count must not be negative")

        flags = 0
        if ignore_case:
            flags |= re.IGNORECASE
        if multiline:
            flags |= re.MULTILINE
        if dotall:
            flags |= re.DOTALL
        try:
            compiled = re.compile(pattern, flags)
        except re.error as error:
            raise ValueError(f"Invalid regular expression: {error}") from error

        text_file = await self.get_text_file(path, text_encoding)
        matches = list(compiled.finditer(text_file.content))
        if not matches:
            raise ValueError("regular expression did not match the file")

        selected = matches if count == 0 else matches[:count]
        try:
            new_text = compiled.sub(replacement, text_file.content, count=count)
        except re.error as error:
            raise ValueError(f"Invalid replacement: {error}") from error
        data = new_text.encode(text_encoding)
        await self.write_file(path, data)
        info = await self.get_info(path)

        match_models = []
        for match in selected:
            start_line, start_column = self._line_column(
                text_file.content, text_file.lines, match.start()
            )
            end_line, end_column = self._line_column(
                text_file.content, text_file.lines, match.end()
            )
            match_models.append(
                TextRegexMatch(
                    start = match.start(),
                    end = match.end(),
                    text = match.group(0),
                    start_line = start_line,
                    start_column = start_column,
                    end_line = end_line,
                    end_column = end_column
                )
            )

        new_lines = new_text.splitlines(keepends = True) or [""]
        if "\r\n" in new_text:
            newline = "\r\n"
        elif "\n" in new_text:
            newline = "\n"
        elif "\r" in new_text:
            newline = "\r"
        else:
            newline = ""

        metadata = TextMetadata(
            path = path,
            encoding = text_encoding,
            byte_size = len(data),
            char_count = len(new_text),
            line_count = len(new_lines),
            newline = newline,
            st_mtime = info.st_mtime,
            st_mode = info.st_mode
        )
        return TextRegexEditResult(
            path = path,
            pattern = pattern,
            replacement = replacement,
            requested_count = count,
            replaced = len(selected),
            matches = match_models,
            char_count = len(new_text),
            line_count = len(new_lines),
            size = len(data),
            metadata = metadata
        )

    async def create_sqlite(self, path: str) -> SQLiteAccess:
        """Create a SQLite database on DataServer and return its access id."""
        response = await self._request(
            "POST",
            "/sqlite/create",
            "SQLite Create",
            json = {"path": path}
        )
        return SQLiteAccess.model_validate(response.json())

    async def open_sqlite(self, path: str) -> SQLiteAccess:
        """Open an existing DataServer SQLite database."""
        response = await self._request(
            "POST",
            "/sqlite/open",
            "SQLite Open",
            json = {"path": path}
        )
        return SQLiteAccess.model_validate(response.json())

    async def execute_sqlite(
        self,
        sqlite_id: str,
        sql: str,
        params: list | dict | None = None
    ) -> SQLiteExecuteResult:
        """Execute one SQL statement against an opened SQLite database."""
        response = await self._request(
            "POST",
            f"/sqlite/{quote(sqlite_id)}/execute",
            "SQLite Execute",
            json = {
                "sql": sql,
                "params": params,
            }
        )
        return SQLiteExecuteResult.model_validate(response.json())

    async def close_sqlite(self, sqlite_id: str) -> None:
        """Close an opened SQLite database and invalidate its access id."""
        await self._request(
            "DELETE",
            f"/sqlite/{quote(sqlite_id)}",
            "SQLite Close"
        )

    async def list_sqlite(self) -> list[SQLiteDatabaseInfo]:
        """List every SQLite database currently open on DataServer."""
        response = await self._request("GET", "/sqlite/list", "SQLite List")
        return [
            SQLiteDatabaseInfo.model_validate(item)
            for item in response.json()
        ]

    async def close(self) -> None:
        await self.client.aclose()
