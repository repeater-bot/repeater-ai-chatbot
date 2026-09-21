from fastapi import APIRouter

models_router = APIRouter(
    prefix = "/models",
    tags = ["models"]
)

refresh_router = APIRouter(
    prefix = "/model_refresh",
    tags = ["model_refresh"]
)