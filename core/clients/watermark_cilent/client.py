import httpx
import string
from ...global_config_manager import ConfigManager, WatermarkCorrectionLevel
from typing import Any, AsyncGenerator
from ...special_exception import HTTPException

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

    async def encode_watermark(
            self,
            text: str,
            block_size: int,
            correction_level: WatermarkCorrectionLevel | float,
            image: bytes,
            output_format: str = ".png"
        ) -> AsyncGenerator[bytes, None]:
        stream_response = self.client.stream(
            method = "POST",
            url = "/watermark/encode",
            data = {
                "text": text,
                "block_size": block_size,
                "correction_level": correction_level.value if isinstance(correction_level, WatermarkCorrectionLevel) else correction_level,
                "file_format": output_format
            },
            files = {
                "file": image,
            }
        )


        async with stream_response as stream:

            if stream.status_code != 200:
                raise HTTPException(stream.text, stream.status_code)
            
            async for byte in stream.aiter_bytes():
                yield byte
            

    async def decode_watermark(
            self,
            image: bytes,
            block_size: int,
            correction_level: WatermarkCorrectionLevel | float,
            bytes_count: int
        ) -> str:
        response = await self.client.post(
            url = "/watermark/decode",
            data = {
                "bytes_count": bytes_count,
                "block_size": block_size,
                "correction_level": correction_level.value if isinstance(correction_level, WatermarkCorrectionLevel) else correction_level,
            },
            files = {
                "file": image,
            }
        )
        if response.status_code != 200:
            raise HTTPException(response.text, response.status_code)
        return response.text

    @classmethod
    def num_to_fixed_str(cls, n: int, width=8):
        result = []
        for _ in range(width):
            result.append(cls.CHARS[n % 62])
            n //= 62
        if n > 0:
            raise ValueError("number too large")
        return ''.join(reversed(result))

    @classmethod
    def fixed_str_to_num(cls, s: str):
        n = 0
        for c in s:
            n = n * 62 + cls.CHARS.index(c)
        return n

    async def encode_text_watermark(self, image: bytes, text: str, output_format: str = ".png") -> AsyncGenerator[bytes, None]:
        configs = ConfigManager.get_configs().watermark

        text_len = len(text.encode("utf-8"))
        text_bytes_count = self.num_to_fixed_str(
            text_len,
            configs.size_header_width
        )
        encode_text = (text_bytes_count + text).ljust(configs.base_size, " ")

        stream = self.encode_watermark(
            text = encode_text,
            block_size = configs.base_size,
            correction_level = configs.correction_level,
            image = image,
            output_format = output_format
        )

        async for byte in stream:
            yield byte

    async def decode_text_watermark(self, image: bytes) -> str:
        configs = ConfigManager.get_configs().watermark

        decode_text = await self.decode_watermark(
            image,
            block_size = configs.base_size,
            correction_level = configs.correction_level,
            bytes_count = configs.base_size
        )

        text_bytes_count = self.fixed_str_to_num(
            decode_text[:configs.size_header_width]
        )
        text = decode_text[
            configs.size_header_width : configs.size_header_width + text_bytes_count
        ]

        return text