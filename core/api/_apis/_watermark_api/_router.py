from .._root import root_router
from fastapi import APIRouter

watermark_router = APIRouter(
    prefix="/watermark",
    tags=["watermark"],
)