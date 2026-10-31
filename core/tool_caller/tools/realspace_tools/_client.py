from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path

from ....global_config_manager import ConfigManager
from ....special_exception import HTTPException


def resolve(path: str, tool_name: str) -> Path:
    if not path or not path.strip():
        raise HTTPException(detail="path cannot be empty", status_code=400)

    operation = tool_name.removeprefix("realspace_")
    field_name = "copy_" if operation == "copy" else operation
    target = Path(path).expanduser().resolve()
    config = ConfigManager.get_configs().tool_calls.tools_configs.realspace

    for unit in config.writelist:
        if not unit.path or not unit.path.strip():
            continue
        root = Path(unit.path).expanduser().resolve()
        if not (target == root or root in target.parents):
            continue
        if not getattr(unit, field_name, False):
            continue
        if target == root and operation not in {
            "read", "exists", "is_file", "is_dir", "glob", "rematch",
            "list", "info", "get_url", "hash", "du", "tree",
        }:
            raise HTTPException(
                detail=f"cannot modify a {tool_name} whitelist root: {target}",
                status_code=403
            )
        return target

    raise HTTPException(
        detail=f"path is outside the {tool_name} whitelist: {target}",
        status_code=403
    )


class RealspaceClient:
    def __init__(self, tool_name: str):
        self.tool_name = tool_name

    def _resolve(self, path: str) -> Path:
        return resolve(path, self.tool_name)

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
        source = self._resolve(path)
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
        source = self._resolve(path)
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


    async def get_file_url(self, path: str) -> str:
        return self._resolve(path).as_uri()


_clients: dict[str, RealspaceClient] = {}


def get_realspace_client(tool_name: str) -> RealspaceClient:
    client = _clients.get(tool_name)
    if client is None:
        client = RealspaceClient(tool_name)
        _clients[tool_name] = client
    return client
