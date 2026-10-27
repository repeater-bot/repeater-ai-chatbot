from fastapi import APIRouter

workspace_router = APIRouter(
    prefix = "/workspace",
    tags = ["workspace"],
)
