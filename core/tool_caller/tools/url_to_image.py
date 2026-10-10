import httpx
import base64
import asyncio
import puremagic

from ...user_data_managers.context import ImageBlock, ImageUrlBlock
from ..framework import ToolsCaller, ToolPackage, RuntimePackage, ContentResult
from pydantic import BaseModel, Field
from ...auxiliary.http import is_public_url

@ToolsCaller.register
class URLToImage(ToolPackage):
    class Params(BaseModel):
        urls: list[str] = Field(..., description="The URLs of the images to read")
    
    name = "url_to_image"
    description = "Read the image content in the URL."
    client: httpx.AsyncClient | None = None

    def __init__(self) -> None:
        self.init_client()

    @classmethod
    def init_client(cls) -> None:
        if not cls.client:
            cls.client = httpx.AsyncClient()

    @staticmethod
    def make_data_url(image: bytes) -> str:
        mime_type = puremagic.from_string(image, mime = True)
        return f"data:{mime_type};base64,{base64.b64encode(image).decode(encoding='utf-8')}"

    @classmethod
    async def fetch_image(cls, url: str) -> bytes:
        if cls.client is None:
            raise RuntimeError("ImageDownloader.client is None")
        response = await cls.client.get(url)
        response.raise_for_status()
        return response.content

    async def call(self, args: Params, runtime: RuntimePackage):
        submited_urls: list[str] = []
        for url in args.urls:
            if await is_public_url(url):
                submited_urls.append(url)
            else:
                image = await self.fetch_image(url)
                data_url = await asyncio.to_thread(
                    self.make_data_url,
                    image
                )
                submited_urls.append(data_url)
                # Frees memory
                del image
        
        return ContentResult(
            content = [
                ImageBlock(
                    image_url = ImageUrlBlock(
                        url = url
                    )
                )
                for url in submited_urls
            ]
        )
