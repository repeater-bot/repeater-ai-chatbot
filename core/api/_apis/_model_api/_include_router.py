from .._root import root_router
from ._router import models_router, refresh_router

root_router.include_router(models_router)
root_router.include_router(refresh_router)