from fastapi import APIRouter

model_router = APIRouter(tags=["model"])

models_router = APIRouter(
    prefix = "/models",
    tags = ["models"]
)

refresh_router = APIRouter(
    prefix = "/model_refresh",
    tags = ["refresh"]
)

model_router.include_router(models_router)
model_router.include_router(refresh_router)