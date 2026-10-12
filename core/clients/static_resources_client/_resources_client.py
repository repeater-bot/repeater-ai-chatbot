import httpx

from urllib.parse import quote
from yarl import URL
from ...special_exception import HTTPException

class StaticResourcesClient:
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
        if isinstance(base_url, str):
            if base_url:
                self._base_url = URL(base_url)
            else:
                raise ValueError("base_url cannot be empty")
        else:
            raise TypeError("base_url must be a string")
        
        self.client = httpx.AsyncClient(
            base_url = str(self._base_url),
            timeout = timeout,
            params = params,
            headers = headers,
            cookies = cookies,
            auth = auth,
            transport = transport
        )
    
    @property
    def base_url(self) -> URL:
        return self._base_url
    
    def str_or_url(self, path: str | URL) -> str:
        if isinstance(path, str):
            return path
        elif isinstance(path, URL):
            return str(path)
        else:
            raise TypeError("path must be a string or URL")
    
    async def get_file(self, path: str | URL) -> bytes:
        """Get a file from the server."""
        try:
            response = await self.client.get(
                quote(self.str_or_url(path))
            )
        except httpx.RequestError as e:
            raise HTTPException(detail = f"Get Static Resource Failed: {e}") from e
        
        response.raise_for_status()
        return response.content
    
    async def get_text(self, path: str | URL, text_encoding: str = "utf-8") -> str:
        """Get a text file from the server."""
        try:
            response = await self.client.get(
                quote(self.str_or_url(path)),
                params = {
                    "text_encoding": text_encoding,
                }
            )
        except httpx.RequestError as e:
            raise HTTPException(detail = f"Get Static Resource Failed: {e}") from e
    
        response.raise_for_status()
        return response.text
    
    async def close(self):
        await self.client.aclose()