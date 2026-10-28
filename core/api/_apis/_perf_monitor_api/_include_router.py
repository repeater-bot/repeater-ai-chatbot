from .._root import root_router
from ._router import perf_monitor_api

root_router.include_router(perf_monitor_api)