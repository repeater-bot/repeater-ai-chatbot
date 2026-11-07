from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path

from ....global_config_manager import ConfigManager
from ....special_exception import HTTPException
from ....clients.data_client import (
    TextEditResult,
    TextFile,
    TextLine,
    TextMetadata,
    TextRegexEditResult,
    TextRegexMatch,
)


READ_OPERATIONS = {
    "read", "read_text", "exists", "is_file", "is_dir", "glob",
    "rematch", "list", "info", "get_url", "hash", "du", "tree",
    "upload_to_workspace",
}


def resolve(path: str, tool_name: str, permission: str | None = None) -> Path:
    if not path or not path.strip():
        raise HTTPException(detail="path cannot be empty", status_code=400)

    operation = tool_name.removeprefix("realspace_")
    access = permission or ("read" if operation in READ_OPERATIONS else "write")
    target = Path(path).expanduser().resolve()
    config = ConfigManager.get_configs().tool_calls.tools_configs.realspace

    for key, unit in config.whitelist.items():
        if not unit.path or not unit.path.strip():
            continue
        root = Path(unit.path).expanduser().resolve()
        if not (target == root or root in target.parents):
            continue
        if not getattr(unit, access, False):
            continue
        if access == "write" and target == root:
            raise HTTPException(
                detail=f"cannot modify a {tool_name} whitelist root ({key}): {target}",
                status_code=403
            )
        return target

    raise HTTPException(
        detail=f"path is outside the {access} whitelist for {tool_name}: {target}",
        status_code=403
    )


class RealspaceClient:
    def __init__(self, tool_name: str):
        self.tool_name = tool_name

    def _resolve(self, path: str, permission: str | None = None) -> Path:
        return resolve(path, self.tool_name, permission)

    async def get_file(self, path: str, start: int | None = None, length: int | None = None, headers=None) -> bytes:
        data = self._resolve(path).read_bytes()
        start = 0 if start is None else start
        return data[start:] if length is None else data[start:start + length]


    async def get_text(self, path: str, text_encoding: str = "utf-8", start=None, length=None, headers=None) -> str:
        return (await self.get_file(path, start, length)).decode(text_encoding)


    async def list_dir(self, path: str = "", recursive: bool = False) -> list[str]:
        target = self._resolve(path)
        if target.is_file():
            raise HTTPException(detail=f"{path} is not a directory", status_code=400)
        items = target.rglob("*") if recursive else target.iterdir()
        return sorted(str(item) for item in items)


    async def glob(self, path: str, pattern: str, recursive: bool = False) -> list[str]:
        target = self._resolve(path)
        if target.is_file():
            raise HTTPException(detail=f"{path} is not a directory", status_code=400)
        return sorted(str(item) for item in target.glob(f"**/{pattern}" if recursive else pattern))


    async def rematch(self, path: str, pattern: str) -> bool:
        target = self._resolve(path)
        try:
            return re.match(pattern, str(target)) is not None
        except re.error as error:
            raise HTTPException(detail=f"Invalid regular expression: {error}", status_code=400) from error


    async def get_info(self, path: str) -> dict:
        stat = self._resolve(path).stat()
        return {
            "size": stat.st_size,
            "st_mtime": stat.st_mtime,
            "st_mtime_ns": stat.st_mtime_ns,
            "st_atime": stat.st_atime,
            "st_atime_ns": stat.st_atime_ns,
            "st_mode": bin(stat.st_mode),
        }


    async def exists(self, path: str) -> bool:
        return self._resolve(path).exists()


    async def is_file(self, path: str) -> bool:
        return self._resolve(path).is_file()


    async def is_dir(self, path: str) -> bool:
        return self._resolve(path).is_dir()


    async def write_file(self, path: str, data: bytes, filename=None, content_type=None) -> int:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return len(data)


    async def append(self, path: str, data: bytes) -> int:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("ab") as file:
            file.write(data)
        return target.stat().st_size


    async def append_text(self, path: str, text: str, text_encoding: str = "utf-8") -> int:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding=text_encoding) as file:
            file.write(text)
        return target.stat().st_size


    async def truncate(self, path: str, size: int) -> int:
        if size < 0:
            raise HTTPException(detail="size must not be negative", status_code=400)
        target = self._resolve(path)
        with target.open("r+b") as file:
            file.truncate(size)
        return size


    async def touch(self, path: str) -> int:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
        return target.stat().st_size


    async def edit(self, path: str, data: bytes, start: int, end: int) -> int:
        target = self._resolve(path)
        content = target.read_bytes()
        if start < 0 or end < start or end > len(content):
            raise HTTPException(detail="invalid byte range", status_code=400)
        target.write_bytes(content[:start] + data + content[end:])
        return target.stat().st_size


    async def delete(self, path: str, recursive: bool = False) -> dict:
        target = self._resolve(path)
        if any(target == root for root in _roots()):
            raise HTTPException(detail="cannot delete a realspace whitelist root", status_code=403)
        if target.is_dir():
            if any(target.iterdir()) and not recursive:
                raise HTTPException(detail=f"Directory {target} is not empty", status_code=409)
            files = sum(1 for item in target.rglob("*") if item.is_file())
            dirs = 1 + sum(1 for item in target.rglob("*") if item.is_dir())
            shutil.rmtree(target)
            return {"deleted_files": files, "deleted_dirs": dirs}
        if not target.exists():
            raise HTTPException(detail=f"File {target} not found", status_code=404)
        target.unlink()
        return {"deleted_files": 1, "deleted_dirs": 0}


    async def mkdir(self, path: str) -> str:
        target = self._resolve(path)
        target.mkdir(parents=True, exist_ok=False)
        return str(target)


    async def move(self, path: str, destination: str) -> dict:
        source = self._resolve(path)
        target = self._resolve(destination)
        if target.exists():
            raise HTTPException(detail=f"{target} already exists", status_code=409)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        return {"source": str(source), "destination": str(target)}


    async def copy(self, path: str, destination: str) -> dict:
        source = self._resolve(path, "read")
        target = self._resolve(destination)
        if target.exists():
            raise HTTPException(detail=f"{target} already exists", status_code=409)
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            files = sum(1 for item in source.rglob("*") if item.is_file())
            dirs = 1 + sum(1 for item in source.rglob("*") if item.is_dir())
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
            files, dirs = 1, 0
        return {"source": str(source), "destination": str(target), "copied_files": files, "copied_dirs": dirs}


    async def copy_range(self, path: str, destination: str, start: int, end: int) -> dict:
        source = self._resolve(path, "read")
        target = self._resolve(destination)
        if target.exists():
            raise HTTPException(detail=f"{target} already exists", status_code=409)
        content = source.read_bytes()
        if start < 0 or end < start or end > len(content):
            raise HTTPException(detail="invalid byte range", status_code=400)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content[start:end])
        return {"source": str(source), "destination": str(target), "size": end - start}


    async def hash(self, path: str, algorithm: str = "sha256") -> dict:
        if algorithm != "sha256":
            raise HTTPException(detail=f"Unsupported hash algorithm: {algorithm}", status_code=400)
        target = self._resolve(path)
        digest = hashlib.sha256()
        with target.open("rb") as file:
            for chunk in iter(lambda: file.read(1 << 20), b""):
                digest.update(chunk)
        return {"algorithm": algorithm, "digest": digest.hexdigest(), "size": target.stat().st_size}


    async def du(self, path: str) -> dict:
        target = self._resolve(path)
        if target.is_file():
            return {"path": str(target), "size": target.stat().st_size, "files": 1, "dirs": 0}
        files = [item for item in target.rglob("*") if item.is_file()]
        dirs = 1 + sum(1 for item in target.rglob("*") if item.is_dir())
        return {"path": str(target), "size": sum(item.stat().st_size for item in files), "files": len(files), "dirs": dirs}


    async def tree(self, path: str, max_depth: int = -1) -> dict:
        if max_depth < -1:
            raise HTTPException(detail="max_depth must be -1 or greater", status_code=400)

        def build(item: Path, depth: int) -> dict:
            if item.is_file():
                return {"path": str(item), "type": "file", "size": item.stat().st_size}
            children = []
            if max_depth == -1 or depth < max_depth:
                children = [build(child, depth + 1) for child in sorted(item.iterdir())]
            return {"path": str(item), "type": "directory", "children": children}

        return build(self._resolve(path), 0)


    @staticmethod
    def _line_column(
        text: str,
        lines: list[TextLine],
        offset: int
    ) -> tuple[int, int]:
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

    async def get_text_file(self, path: str, text_encoding: str = "utf-8") -> TextFile:
        """Read a real text file and compute lines/offsets client-side."""
        target = self._resolve(path)
        data = target.read_bytes()
        text = data.decode(text_encoding)
        stat = target.stat()

        lines: list[TextLine] = []
        offset = 0
        for number, raw_line in enumerate(text.splitlines(keepends=True) or [""], start=1):
            if raw_line.endswith("\r\n"):
                content, ending = raw_line[:-2], "\r\n"
            elif raw_line.endswith("\n") or raw_line.endswith("\r"):
                content, ending = raw_line[:-1], raw_line[-1]
            else:
                content, ending = raw_line, ""
            start = offset
            end = start + len(content)
            offset += len(raw_line)
            lines.append(TextLine(
                number=number, start=start, end=end, raw_end=offset,
                text=content, ending=ending
            ))

        if "\r\n" in text:
            newline = "\r\n"
        elif "\n" in text:
            newline = "\n"
        elif "\r" in text:
            newline = "\r"
        else:
            newline = ""

        metadata = TextMetadata(
            path=path, encoding=text_encoding, byte_size=len(data),
            char_count=len(text), line_count=len(lines), newline=newline,
            st_mtime=stat.st_mtime, st_mode=bin(stat.st_mode)
        )
        return TextFile(
            content=text,
            numbered_content="".join(
                f"{line.number:>4} | {line.text}{line.ending}" for line in lines
            ),
            lines=lines, metadata=metadata
        )

    async def _commit_text_edit(
        self, path: str, text_file: TextFile, replacement: str,
        start: int, end: int, mode: str, text_encoding: str
    ) -> TextEditResult:
        if start < 0 or end < start or end > len(text_file.content):
            raise ValueError("invalid character range")
        new_text = text_file.content[:start] + replacement + text_file.content[end:]
        data = new_text.encode(text_encoding)
        target = self._resolve(path)
        target.write_bytes(data)
        stat = target.stat()

        start_line, start_column = self._line_column(text_file.content, text_file.lines, start)
        end_line, end_column = self._line_column(text_file.content, text_file.lines, end)
        new_lines = new_text.splitlines(keepends=True) or [""]
        metadata = TextMetadata(
            path=path, encoding=text_encoding, byte_size=len(data),
            char_count=len(new_text), line_count=len(new_lines),
            newline="\r\n" if "\r\n" in new_text else "\n" if "\n" in new_text else "\r" if "\r" in new_text else "",
            st_mtime=stat.st_mtime, st_mode=bin(stat.st_mode)
        )
        return TextEditResult(
            path=path, mode=mode, start_char=start, end_char=end,
            start_line=start_line, start_column=start_column,
            end_line=end_line, end_column=end_column,
            replaced_chars=end - start, char_count=len(new_text),
            line_count=len(new_lines), size=len(data), metadata=metadata
        )

    async def edit_text_by_char(self, path: str, replacement: str, start: int, end: int | None = None, text_encoding: str = "utf-8") -> TextEditResult:
        end = start if end is None else end
        text_file = await self.get_text_file(path, text_encoding)
        return await self._commit_text_edit(path, text_file, replacement, start, end, "char", text_encoding)

    async def edit_text_by_line(self, path: str, replacement: str, start_line: int = 1, start_column: int = 1, end_line: int | None = None, end_column: int | None = None, text_encoding: str = "utf-8") -> TextEditResult:
        end_line = start_line if end_line is None else end_line
        end_column = start_column if end_column is None else end_column
        text_file = await self.get_text_file(path, text_encoding)
        start = self._text_offset(text_file.content, text_file.lines, start_line, start_column)
        end = self._text_offset(text_file.content, text_file.lines, end_line, end_column)
        return await self._commit_text_edit(path, text_file, replacement, start, end, "line", text_encoding)

    @staticmethod
    def _text_offset(text: str, lines: list[TextLine], line: int, column: int) -> int:
        if line == len(lines) + 1 and column == 1:
            return len(text)
        if line < 1 or line > len(lines):
            raise ValueError(f"line must be between 1 and {len(lines)}")
        target = lines[line - 1]
        max_column = target.end - target.start + 1
        if column < 1 or column > max_column:
            raise ValueError(f"column must be between 1 and {max_column} for line {line}")
        return target.start + column - 1

    async def edit_text(self, path: str, replacement: str, start_char: int | None = None, end_char: int | None = None, start_line: int | None = None, start_column: int = 1, end_line: int | None = None, end_column: int | None = None, text_encoding: str = "utf-8") -> TextEditResult:
        if start_char is None and start_line is None:
            raise ValueError("start_char or start_line is required")
        text_file = await self.get_text_file(path, text_encoding)
        both = start_char is not None and start_line is not None
        char_start = start_char
        char_end = (start_char if end_char is None else end_char) if start_char is not None else None
        if start_line is not None:
            end_line = start_line if end_line is None else end_line
            end_column = start_column if end_column is None else end_column
            line_start = self._text_offset(text_file.content, text_file.lines, start_line, start_column)
            line_end = self._text_offset(text_file.content, text_file.lines, end_line, end_column)
        else:
            line_start = line_end = None
        if both:
            if char_start != line_start or char_end != line_end:
                raise ValueError("character and line/column positions do not match")
            start, end, mode = char_start, char_end, "both"
        elif char_start is not None:
            start, end, mode = char_start, char_end, "char"
        else:
            start, end, mode = line_start, line_end, "line"
        return await self._commit_text_edit(path, text_file, replacement, start, end, mode, text_encoding)

    async def insert_text(self, path: str, text: str, line: int = 1, column: int = 1, text_encoding: str = "utf-8") -> TextEditResult:
        return await self.edit_text_by_line(path, text, line, column, line, column, text_encoding)

    async def insert_text_by_char(self, path: str, text: str, char: int, text_encoding: str = "utf-8") -> TextEditResult:
        return await self.edit_text_by_char(path, text, char, char, text_encoding)

    async def delete_text(self, path: str, start_line: int, start_column: int, end_line: int, end_column: int, text_encoding: str = "utf-8") -> TextEditResult:
        return await self.edit_text_by_line(path, "", start_line, start_column, end_line, end_column, text_encoding)

    async def delete_text_by_char(self, path: str, start: int, end: int, text_encoding: str = "utf-8") -> TextEditResult:
        return await self.edit_text_by_char(path, "", start, end, text_encoding)

    async def edit_text_regex(self, path: str, pattern: str, replacement: str, count: int = 1, ignore_case: bool = False, multiline: bool = False, dotall: bool = False, text_encoding: str = "utf-8") -> TextRegexEditResult:
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
        new_text = compiled.sub(replacement, text_file.content, count=count)
        data = new_text.encode(text_encoding)
        target = self._resolve(path)
        target.write_bytes(data)
        stat = target.stat()

        match_models = []
        for match in selected:
            start_line, start_column = self._line_column(text_file.content, text_file.lines, match.start())
            end_line, end_column = self._line_column(text_file.content, text_file.lines, match.end())
            match_models.append(TextRegexMatch(
                start=match.start(), end=match.end(), text=match.group(0),
                start_line=start_line, start_column=start_column,
                end_line=end_line, end_column=end_column
            ))
        new_lines = new_text.splitlines(keepends=True) or [""]
        metadata = TextMetadata(
            path=path, encoding=text_encoding, byte_size=len(data),
            char_count=len(new_text), line_count=len(new_lines),
            newline="\r\n" if "\r\n" in new_text else "\n" if "\n" in new_text else "\r" if "\r" in new_text else "",
            st_mtime=stat.st_mtime, st_mode=bin(stat.st_mode)
        )
        return TextRegexEditResult(
            path=path, pattern=pattern, replacement=replacement,
            requested_count=count, replaced=len(selected), matches=match_models,
            char_count=len(new_text), line_count=len(new_lines),
            size=len(data), metadata=metadata
        )

    async def get_file_url(self, path: str) -> str:
        return self._resolve(path).as_uri()


_clients: dict[str, RealspaceClient] = {}


def get_realspace_client(tool_name: str) -> RealspaceClient:
    client = _clients.get(tool_name)
    if client is None:
        client = RealspaceClient(tool_name)
        _clients[tool_name] = client
    return client
