from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class SandboxMode(StrEnum):
    READ_ONLY = "read_only"
    PATH_WRITE = "path_write"
    FULL_ACCESS = "full_access"


class SandboxUnavailable(RuntimeError):
    """Raised when the requested confinement cannot be enforced."""


@dataclass
class ShellResult:
    command: str
    cwd: str
    mode: str
    exit_code: int
    stdout: str
    stderr: str
    denied: bool = False
    backend: str = "local"
    encoding: str = "utf-8"
    extra: dict = field(default_factory = dict)


@dataclass
class ShellRequest:
    command: str
    cwd: str
    mode: SandboxMode
    timeout: float = 30
    encoding: str = "utf-8"
