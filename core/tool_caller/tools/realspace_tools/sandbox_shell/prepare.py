from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from loguru import logger


async def prepare_shell_root(path: Path, enabled: bool) -> None:
    """Prepare the shell root before confinement.

    Windows lowers the directory tree to Low integrity. Linux and macOS have no
    Windows integrity levels; their confinement grants path access in bwrap /
    Seatbelt instead, so this hook only records the preparation step.
    """
    if not enabled:
        return

    if sys.platform == "win32":
        from .windows_acl import lower_integrity
        await asyncio.to_thread(lower_integrity, str(path))
        return

    logger.info(
        "Preparing realspace shell root on %s (integrity levels not applicable): %s",
        sys.platform,
        path,
    )
