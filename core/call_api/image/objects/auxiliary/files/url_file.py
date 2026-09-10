import httpx

from pydantic import BaseModel
from typing import Literal
from loguru import logger
from ......special_exception import HTTPException

class UrlFile(BaseModel):
    type: Literal["url"] = "url"
    url: str

    async def get_file(self) -> bytes:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url)
            logger.error(
                "Server could not successfully retrieve the data provided."
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code = 400,
                    detail = "Server could not successfully retrieve the data provided, please check the url and try again."
                )
            return response.content
