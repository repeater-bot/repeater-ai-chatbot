from fastapi import APIRouter

sqlite_router = APIRouter(
    prefix = "/data_server/sqlite",
    tags = ["data_server", "sqlite"],
)
