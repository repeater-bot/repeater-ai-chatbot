import aiofiles

from pydantic import BaseModel
from typing import Literal
from loguru import logger
from ......special_exception import HTTPException

class PathFile(BaseModel):
    type: Literal["path"] = "path"
    path: str

    async def get_file(self) -> bytes:
        try:
            async with aiofiles.open(self.path, "rb") as file:
                return await file.read()
        except Exception as e:
            logger.exception(
                "Server could not successfully retrieve the data provided."
            )
            raise HTTPException(
                status_code = 400,
                detail = "Server could not successfully retrieve the data provided, please check the path and try again."
            ) from e