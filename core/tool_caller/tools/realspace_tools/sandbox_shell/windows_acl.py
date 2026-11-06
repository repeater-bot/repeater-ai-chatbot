from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import os
import random
import subprocess
import tempfile
from pathlib import Path

from .base import SandboxMode, SandboxUnavailable, ShellRequest, ShellResult

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)

TOKEN_ALL_ACCESS = 0xF01FF
LUA_TOKEN = 0x4
DISABLE_MAX_PRIVILEGE = 0x1
WRITE_RESTRICTED = 0x8

GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x1
FILE_SHARE_WRITE = 0x2
CREATE_ALWAYS = 2
FILE_ATTRIBUTE_NORMAL = 0x80
STARTF_USESTDHANDLES = 0x100
CREATE_UNICODE_ENVIRONMENT = 0x400
INFINITE = 0xFFFFFFFF
WAIT_TIMEOUT = 0x102
STILL_ACTIVE = 259


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", wt.DWORD),
        ("lpSecurityDescriptor", ctypes.c_void_p),
        ("bInheritHandle", wt.BOOL),
    ]


class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wt.DWORD), ("lpReserved", wt.LPWSTR), ("lpDesktop", wt.LPWSTR),
        ("lpTitle", wt.LPWSTR), ("dwX", wt.DWORD), ("dwY", wt.DWORD),
        ("dwXSize", wt.DWORD), ("dwYSize", wt.DWORD),
        ("dwXCountChars", wt.DWORD), ("dwYCountChars", wt.DWORD),
        ("dwFillAttribute", wt.DWORD), ("dwFlags", wt.DWORD),
        ("wShowWindow", wt.WORD), ("cbReserved2", wt.WORD),
        ("lpReserved2", ctypes.c_void_p), ("hStdInput", wt.HANDLE),
        ("hStdOutput", wt.HANDLE), ("hStdError", wt.HANDLE),
    ]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wt.HANDLE), ("hThread", wt.HANDLE),
        ("dwProcessId", wt.DWORD), ("dwThreadId", wt.DWORD),
    ]


class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Sid", ctypes.c_void_p), ("Attributes", wt.DWORD)]


kernel32.CreateFileW.argtypes = [
    wt.LPCWSTR, wt.DWORD, wt.DWORD, ctypes.POINTER(SECURITY_ATTRIBUTES),
    wt.DWORD, wt.DWORD, wt.HANDLE,
]
kernel32.CreateFileW.restype = wt.HANDLE
advapi32.OpenProcessToken.argtypes = [wt.HANDLE, wt.DWORD, ctypes.POINTER(wt.HANDLE)]
advapi32.CreateRestrictedToken.argtypes = [
    wt.HANDLE, wt.DWORD, wt.DWORD, ctypes.POINTER(SID_AND_ATTRIBUTES),
    wt.DWORD, ctypes.c_void_p, wt.DWORD, ctypes.POINTER(SID_AND_ATTRIBUTES),
    ctypes.POINTER(wt.HANDLE),
]
advapi32.ConvertStringSidToSidW.argtypes = [wt.LPCWSTR, ctypes.POINTER(ctypes.c_void_p)]
advapi32.CreateProcessAsUserW.argtypes = [
    wt.HANDLE, wt.LPCWSTR, wt.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
    wt.BOOL, wt.DWORD, ctypes.c_void_p, wt.LPCWSTR,
    ctypes.POINTER(STARTUPINFOW), ctypes.POINTER(PROCESS_INFORMATION),
]
kernel32.WaitForSingleObject.argtypes = [wt.HANDLE, wt.DWORD]
kernel32.GetExitCodeProcess.argtypes = [wt.HANDLE, ctypes.POINTER(wt.DWORD)]
kernel32.TerminateProcess.argtypes = [wt.HANDLE, ctypes.c_uint]
kernel32.CloseHandle.argtypes = [wt.HANDLE]
kernel32.GetCurrentProcess.restype = wt.HANDLE
kernel32.LocalFree.argtypes = [ctypes.c_void_p]
kernel32.LocalFree.restype = ctypes.c_void_p


def _fail(name: str) -> None:
    raise SandboxUnavailable(f"{name} failed: {ctypes.get_last_error()}")


def _logon_sid() -> str:
    """Return the current token's logon SID (stable, valid for restricting SIDs)."""
    output = subprocess.check_output(
        ["whoami", "/logonid"],
        text = True,
        encoding = "utf-8",
        errors = "replace",
    )
    for token in output.split():
        if token.startswith("S-1-5-5-"):
            return token
    raise SandboxUnavailable("could not determine the current logon SID")


def run_windows_acl(request: ShellRequest) -> ShellResult:
    if request.mode == SandboxMode.FULL_ACCESS:
        raise SandboxUnavailable("full_access must not use the ACL backend")

    tmp = Path(tempfile.mkdtemp(prefix = "dsh-shell-"))
    out_path, err_path = tmp / "out.txt", tmp / "err.txt"
    sa = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, True)
    out_handle = kernel32.CreateFileW(
        str(out_path), GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE,
        ctypes.byref(sa), CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, None,
    )
    err_handle = kernel32.CreateFileW(
        str(err_path), GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE,
        ctypes.byref(sa), CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, None,
    )
    if out_handle in (None, wt.HANDLE(-1).value) or err_handle in (None, wt.HANDLE(-1).value):
        _fail("CreateFileW")

    token = wt.HANDLE()
    restricted = wt.HANDLE()
    sid_ptr = ctypes.c_void_p()
    grant_sid = None
    try:
        if not advapi32.OpenProcessToken(
            kernel32.GetCurrentProcess(), TOKEN_ALL_ACCESS, ctypes.byref(token)
        ):
            _fail("OpenProcessToken")

        sids = (SID_AND_ATTRIBUTES * 1)()
        sid_count = 0
        if request.mode == SandboxMode.PATH_WRITE:
            grant_sid = _logon_sid()
            if not advapi32.ConvertStringSidToSidW(grant_sid, ctypes.byref(sid_ptr)):
                _fail("ConvertStringSidToSidW")
            sids[0].Sid = sid_ptr
            sids[0].Attributes = 0
            sid_count = 1
            grant = subprocess.run(
                ["icacls", request.cwd, "/grant", f"*{grant_sid}:(OI)(CI)M"],
                capture_output = True, text = True,
            )
            if grant.returncode != 0:
                raise SandboxUnavailable(f"icacls grant failed: {grant.stderr or grant.stdout}")

        flags = DISABLE_MAX_PRIVILEGE | WRITE_RESTRICTED
        if not advapi32.CreateRestrictedToken(
            token, flags, 0, None, 0, None, sid_count,
            sids if sid_count else None, ctypes.byref(restricted)
        ):
            _fail("CreateRestrictedToken")

        startup = STARTUPINFOW()
        startup.cb = ctypes.sizeof(startup)
        startup.dwFlags = STARTF_USESTDHANDLES
        startup.hStdOutput = out_handle
        startup.hStdError = err_handle
        startup.hStdInput = None
        process_info = PROCESS_INFORMATION()
        command_line = ctypes.create_unicode_buffer(
            f'cmd.exe /d /s /c "{request.command}"'
        )
        if not advapi32.CreateProcessAsUserW(
            restricted, None, command_line, None, None, True,
            CREATE_UNICODE_ENVIRONMENT, None, request.cwd,
            ctypes.byref(startup), ctypes.byref(process_info)
        ):
            _fail("CreateProcessAsUserW")

        wait_ms = int(request.timeout * 1000)
        wait_result = kernel32.WaitForSingleObject(process_info.hProcess, wait_ms)
        timed_out = wait_result == WAIT_TIMEOUT
        if timed_out:
            kernel32.TerminateProcess(process_info.hProcess, 124)
            kernel32.WaitForSingleObject(process_info.hProcess, INFINITE)

        exit_code = wt.DWORD(0)
        kernel32.GetExitCodeProcess(process_info.hProcess, ctypes.byref(exit_code))
        stdout = out_path.read_text(encoding = "utf-8", errors = "replace")
        stderr = err_path.read_text(encoding = "utf-8", errors = "replace")
        denied = exit_code.value != 0 and (
            "access is denied" in stderr.lower()
            or "拒绝访问" in stderr
        )
        if timed_out:
            stderr += f"\nshell timed out after {request.timeout}s"
        return ShellResult(
            command = request.command, cwd = request.cwd, mode = request.mode.value,
            exit_code = 124 if timed_out else exit_code.value,
            stdout = stdout, stderr = stderr, denied = denied,
            backend = "windows-acl",
        )
    finally:
        for handle in (out_handle, err_handle, token, restricted):
            try:
                if handle not in (None, wt.HANDLE(-1).value):
                    kernel32.CloseHandle(handle)
            except Exception:
                pass
        if sid_ptr:
            kernel32.LocalFree(sid_ptr)
        if grant_sid:
            subprocess.run(
                ["icacls", request.cwd, "/remove:g", f"*{grant_sid}"],
                capture_output = True, text = True,
            )
        try:
            out_path.unlink(missing_ok = True)
            err_path.unlink(missing_ok = True)
            tmp.rmdir()
        except OSError:
            pass
