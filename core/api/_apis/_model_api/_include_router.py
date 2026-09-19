from .._root import root_router
from ._router import model_router

root_router.include_router(model_router)