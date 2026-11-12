from . import _routes  # noqa: F401  (importing the package registers routes)
from .sqlite import sqlite_router
from .._root import root_router
from ._router import workspace_router

root_router.include_router(workspace_router)
root_router.include_router(sqlite_router)
