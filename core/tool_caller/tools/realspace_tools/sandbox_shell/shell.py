from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from pydantic import BaseModel, Field

from ....framework import ToolsCaller, ToolPackage, RuntimePackage
from .base import SandboxMode, SandboxUnavailable, ShellRequest
from .local import run_shell


@ToolsCaller.register
class SandboxShell(ToolPackage):
    class Params(BaseModel):
        path_key: str = Field(..., description="realspace.whitelist key selecting the path and shell_level.")
        command: str = Field(..., description="Shell command to run.")
        cwd: str | None = Field(
            default = None,
            description="Working directory inside the selected path; relative paths resolve against it."
        )
        timeout: float | None = Field(
            default = None,
            ge = 0.1,
            description = "Optional per-call timeout in seconds; defaults to 30."
        )

    name = "sandbox_shell"
    description = "Run a shell command under the shell_level of the selected realspace whitelist entry."

    async def call(self, args: Params, runtime: RuntimePackage):
        realspace = runtime.global_configs.tool_calls.tools_configs.realspace
        unit = realspace.whitelist.get(args.path_key)
        if unit is None:
            raise PermissionError(f"realspace.whitelist has no key {args.path_key!r}")

        root = Path(unit.path).expanduser().resolve()
        if args.cwd is None:
            cwd = root
        else:
            candidate = Path(args.cwd).expanduser()
            cwd = (candidate if candidate.is_absolute() else root / candidate).resolve()
        if not (cwd == root or root in cwd.parents):
            raise PermissionError(f"cwd is outside the {args.path_key!r} whitelist root")
        if not cwd.is_dir():
            raise NotADirectoryError(f"cwd is not a directory: {cwd}")

        level = unit.shell_level.value
        if level == "off":
            raise PermissionError(f"shell is disabled for whitelist {args.path_key!r}")
        if level not in {"read_only", "path_write", "full_access"}:
            raise SandboxUnavailable(f"unknown shell_level {level!r} for {args.path_key!r}")

        result = await run_shell(
            ShellRequest(
                command = args.command,
                cwd = str(cwd),
                mode = SandboxMode(level),
                timeout = args.timeout or 30,
            )
        )
        return asdict(result)
