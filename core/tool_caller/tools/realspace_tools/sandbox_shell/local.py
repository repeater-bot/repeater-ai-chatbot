from __future__ import annotations

import asyncio
import shutil
import sys

from .base import SandboxMode, SandboxUnavailable, ShellRequest, ShellResult


def _shell_argv(command: str) -> list[str]:
    if sys.platform == "win32":
        return ["cmd.exe", "/d", "/s", "/c", command]
    return ["/bin/sh", "-lc", command]


async def _run_local(request: ShellRequest) -> ShellResult:
    process = await asyncio.create_subprocess_exec(
        *_shell_argv(request.command),
        cwd = request.cwd,
        stdout = asyncio.subprocess.PIPE,
        stderr = asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), request.timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise
    return ShellResult(
        command = request.command,
        cwd = request.cwd,
        mode = request.mode.value,
        exit_code = process.returncode or 0,
        stdout = stdout.decode(request.encoding, "replace"),
        stderr = stderr.decode(request.encoding, "replace"),
        backend = "local",
        encoding = request.encoding,
    )


def _bwrap_argv(request: ShellRequest) -> list[str]:
    argv = [
        "bwrap",
        "--die-with-parent",
        "--unshare-all",
        "--proc", "/proc",
        "--dev", "/dev",
        "--ro-bind", "/", "/",
        "--chdir", request.cwd,
    ]
    if request.mode == SandboxMode.PATH_WRITE:
        argv.extend(["--bind", request.cwd, request.cwd])
    argv.extend(["--", *_shell_argv(request.command)])
    return argv


async def _run_bwrap(request: ShellRequest) -> ShellResult:
    if shutil.which("bwrap") is None:
        raise SandboxUnavailable("bwrap is not installed")
    process = await asyncio.create_subprocess_exec(
        *_bwrap_argv(request),
        cwd = request.cwd,
        stdout = asyncio.subprocess.PIPE,
        stderr = asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), request.timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise
    return ShellResult(
        command = request.command,
        cwd = request.cwd,
        mode = request.mode.value,
        exit_code = process.returncode or 0,
        stdout = stdout.decode(request.encoding, "replace"),
        stderr = stderr.decode(request.encoding, "replace"),
        backend = "bwrap",
        encoding = request.encoding,
    )


def _seatbelt_profile(request: ShellRequest) -> str:
    lines = ["(version 1)", "(deny file-write*)", "(allow process*)", "(allow file-read*)"]
    if request.mode == SandboxMode.PATH_WRITE:
        lines.append(f'(allow file-write* (subpath "{request.cwd}"))')
    return "\n".join(lines)


async def _run_seatbelt(request: ShellRequest) -> ShellResult:
    if shutil.which("sandbox-exec") is None:
        raise SandboxUnavailable("sandbox-exec is not available")
    process = await asyncio.create_subprocess_exec(
        "sandbox-exec", "-p", _seatbelt_profile(request), *_shell_argv(request.command),
        cwd = request.cwd,
        stdout = asyncio.subprocess.PIPE,
        stderr = asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), request.timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise
    return ShellResult(
        command = request.command,
        cwd = request.cwd,
        mode = request.mode.value,
        exit_code = process.returncode or 0,
        stdout = stdout.decode(request.encoding, "replace"),
        stderr = stderr.decode(request.encoding, "replace"),
        backend = "seatbelt",
        encoding = request.encoding,
    )


async def run_shell(request: ShellRequest) -> ShellResult:
    if request.mode == SandboxMode.FULL_ACCESS:
        return await _run_local(request)

    if sys.platform == "win32":
        from .windows_acl import run_windows_acl
        return await asyncio.to_thread(run_windows_acl, request)

    if sys.platform.startswith("linux"):
        return await _run_bwrap(request)

    if sys.platform == "darwin":
        return await _run_seatbelt(request)

    raise SandboxUnavailable(f"no sandbox backend for platform {sys.platform!r}")
