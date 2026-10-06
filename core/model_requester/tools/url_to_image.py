import httpx
import base64
import socket
import asyncio
import puremagic

from ...context import ToolCallPackage, ImageBlock, ImageUrlBlock, ContentResult, CallMode
from .._caller import ModelRequester
from pydantic import BaseModel, Field
from urllib.parse import urlsplit
from ipaddress import ip_address
from ...auxiliary.http import is_public_url

@ModelRequester.reg_global_package
class URLToImage(ToolCallPackage):
    class Params(BaseModel):
        urls: list[str] = Field(..., description="The URLs of the images to read")
    
    name = "url_to_image"
    description = "Read the image content in the URL."
    call_mode = CallMode.ASYNC
    client: httpx.AsyncClient | None = None

    @classmethod
    def init_client(cls) -> None:
        if not cls.client:
            cls.client = httpx.AsyncClient()

    def __post_init__(self):
        self.init_client()

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

    async def call(self, args: Params):
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