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
from ._assists import AddrInfo

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
    async def is_public_url(url: str) -> bool:
        u = urlsplit(url)
        if u.scheme not in ("http", "https") or not u.hostname:
            raise ValueError("Invalid URL")

        host = u.hostname
        port = u.port or (443 if u.scheme == "https" else 80)
        
        try:
            ip = ip_address(u.hostname)
            if not ip.is_global:
                return True
        except socket.gaierror:
                # is not an ip address
                # try to DNS resolve
                loop = asyncio.get_event_loop()
                addrs: list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int] | tuple[str, int, int, int] | tuple[int, bytes]]] = await loop.getaddrinfo(
                    host,
                    port,
                    type = socket.SOCK_STREAM
                )
                for addr in addrs:
                    addr_info = AddrInfo.from_addr(addr)
                    if not addr_info.ip_address.is_global:
                        return True
        return False

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
            if await self.is_public_url(url):
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