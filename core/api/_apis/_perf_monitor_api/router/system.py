import os
import sys
import psutil
import getpass
import sysconfig
import platform
from .....global_config_manager import ConfigManager
from typing import Any
from .._router import perf_monitor_api
from ....._info import (
    __version__,
    __author__,
    __license__,
    __copyright__,
    __github__
)

@perf_monitor_api.get("/system")
async def monitor_system():
    """
    Monitor System Usage
    """
    pid = os.getpid()
    process = psutil.Process(pid)
    configs = ConfigManager.get_configs()
    result: dict[str, Any] = {
        "name": configs.system_identification.system_name,
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "copyright": __copyright__,
        "github": __github__,
        "system_identificationConfig": configs.system_identification.model_dump(),
        "platform": {
            "os": os.name,
            "system": sys.platform,
            "platform": sysconfig.get_platform(),
            "name": platform.system(),
            "platform": platform.platform(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "interpreter": {
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
                "releaselevel": sys.version_info.releaselevel,
                "serial": sys.version_info.serial
            },
            "hexversion": sys.hexversion,
            "api_version": sys.api_version,
            "executable": sys.executable,
            "prefix": sys.prefix,
            "base_prefix": sys.base_prefix,
            "exec_prefix": sys.exec_prefix,
            "base_exec_prefix": sys.base_exec_prefix,
            "byteorder": sys.byteorder,
            "copyright": sys.copyright,
            "path": sys.path,
            "flags": {
                "debug": sys.flags.debug,
                "dev_mode": sys.flags.dev_mode,
                "bytes_warning": sys.flags.bytes_warning,
                "dont_write_bytecode": sys.flags.dont_write_bytecode,
                "hash_randomization": sys.flags.hash_randomization,
                "ignore_environment": sys.flags.ignore_environment,
                "inspect": sys.flags.inspect,
                "int_max_str_digits": sys.flags.int_max_str_digits,
                "interactive": sys.flags.interactive,
                "isolated": sys.flags.isolated,
                "no_site": sys.flags.no_site,
                "no_user_site": sys.flags.no_user_site,
                "optimize": sys.flags.optimize,
                "quiet": sys.flags.quiet,
                "safe_path": sys.flags.safe_path,
                "utf8_mode": sys.flags.utf8_mode,
                "verbose": sys.flags.verbose,
                "warn_default_encoding": sys.flags.warn_default_encoding,
            },
            "int_info": {
                "bits_per_digit": sys.int_info.bits_per_digit,
                "sizeof_digit": sys.int_info.sizeof_digit,
                "default_max_str_digits": sys.int_info.default_max_str_digits,
                "str_digits_check_threshold": sys.int_info.str_digits_check_threshold,
            },
            "float_info": {
                "max": sys.float_info.max,
                "max_exp": sys.float_info.max_exp,
                "max_10_exp": sys.float_info.max_10_exp,
                "min": sys.float_info.min,
                "min_exp": sys.float_info.min_exp,
                "min_10_exp": sys.float_info.min_10_exp,
                "dig": sys.float_info.dig,
                "mant_dig": sys.float_info.mant_dig,
                "epsilon": sys.float_info.epsilon,
                "radix": sys.float_info.radix,
                "rounds": sys.float_info.rounds,
            },
            "hash_info": {
                "width": sys.hash_info.width,
                "modulus": sys.hash_info.modulus,
                "inf": sys.hash_info.inf,
                "nan": sys.hash_info.nan,
                "imag": sys.hash_info.imag,
                "algorithm": sys.hash_info.algorithm,
                "hash_bits": sys.hash_info.hash_bits,
                "seed_bits": sys.hash_info.seed_bits,
            },
            "pid": pid,
            "ppid": os.getppid(),
            "cwd": os.getcwd(),
            "user": getpass.getuser(),
            "net_connections": [
                {
                    "fd": c.fd,
                    "family": c.family.name,
                    "laddr_ip": c.laddr.ip if c.laddr else None,
                    "laddr_port": c.laddr.port if c.laddr else None,
                    "raddr_ip": c.raddr.ip if c.raddr else None,
                    "raddr_port": c.raddr.port if c.raddr else None,
                    "type": c.type.name,
                    "status": c.status
                }
                for c in process.net_connections(kind="all")
                if c.status == psutil.CONN_LISTEN
            ],
            "getrecursionlimit": sys.getrecursionlimit(),
            "maxsize": sys.maxsize,
            "fsencoding": sys.getfilesystemencoding(),
            "architecture": list(platform.architecture()),
            "python_version": {
                "implementation": platform.python_implementation(),
                "version": platform.python_version(),
                "compiler": platform.python_compiler(),
                "build": list(platform.python_build()),
                "branch": platform.python_branch(),
                "revision": platform.python_revision()
            }
        }
    }
    return result
