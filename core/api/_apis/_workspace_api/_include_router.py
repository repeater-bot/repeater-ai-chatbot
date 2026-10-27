from . import _routes  # noqa: F401  (importing the package registers routes)
from .._root import root_router
from ._router import workspace_router

root_router.include_router(workspace_router)
