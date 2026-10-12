from .._root import root_router
from ._router import watermark_router

root_router.include_router(watermark_router)