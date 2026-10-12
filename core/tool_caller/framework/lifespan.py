from fastapi import FastAPI
from .caller import ToolsCaller
from ...lifespan import FastAPIStartHandler, FastAPIExitHandler

@FastAPIStartHandler.add_function
async def start(app: FastAPI) -> None:
    await ToolsCaller.start()

@FastAPIExitHandler.add_function
async def stop(app: FastAPI) -> None:
    await ToolsCaller.stop()