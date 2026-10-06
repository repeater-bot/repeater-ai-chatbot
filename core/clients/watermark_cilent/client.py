import httpx
import string
from ...global_config_manager import ConfigManager
from typing import Any, AsyncGenerator

class WatermarkClient:
    CHARS = string.digits + string.ascii_letters

    def __init__(
            self,
            base_url: str,
            timeout: int | float | None = None,
            params: dict[str, str | int | float | bool | None] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            auth: tuple[str, str] | None = None,
            transport: httpx.AsyncHTTPTransport | None = None,
        ):
        
        self.client = httpx.AsyncClient(
            base_url = base_url,
            timeout = timeout,
            params = params,
            headers = headers,
            cookies = cookies,
            auth = auth,
            transport = transport
        )

    async def encode_watermark(self, text: str, image: bytes, output_format: str = ".png") -> AsyncGenerator[bytes, None]:
        stream_response = self.client.stream(
            method = "POST",
            url = "/watermark/encode",
            json = {
                "text": text,
                "output_format": output_format
            },
            files = {
                "file": image,
            }
        )

        async with stream_response as stream:
            async for byte in stream.aiter_bytes():
                yield byte
            

    async def decode_watermark(self, image: bytes, bytes_count: int) -> str:
        response = await self.client.post(
            url = "/watermark/decode",
            json = {
                "bytes_count": bytes_count
            },
            files = {
                "file": image,
            }
        )
        return response.text

    @classmethod
    def num_to_fixed_str(cls, n: int, width=8):
        result = []
        for _ in range(width):
            result.append(cls.CHARS[n % 62])
            n //= 62
        return ''.join(reversed(result))

    @classmethod
    def fixed_str_to_num(cls, s: str):
        n = 0
        for c in s:
            n = n * 62 + cls.CHARS.index(c)
        return n

    async def encode_text_watermark(self, image: bytes, text: str, output_format: str = ".png") -> AsyncGenerator[bytes, None]:
        configs = ConfigManager.get_configs().watermark

        text_len = len(text)
        text_bytes_count = self.num_to_fixed_str(
            text_len,
            configs.size_header_width
        )
        encode_text = (text_bytes_count + text).ljust(configs.base_size, ' ')

        stream = self.encode_watermark(
            encode_text,
            image,
            output_format
        )

        async for byte in stream:
            yield byte

    async def decode_text_watermark(self, image: bytes) -> str:
        configs = ConfigManager.get_configs().watermark

        decode_text = await self.decode_watermark(
            image,
            configs.base_size
        )

        text_bytes_count = self.fixed_str_to_num(
            decode_text[:configs.size_header_width]
        )
        text = decode_text[
            configs.size_header_width : configs.size_header_width + text_bytes_count
        ]

        return text