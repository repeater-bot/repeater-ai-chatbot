import httpx
from ._model import RenderResponse
from ...http_response import Response

class HTMLRenderClient:
    def __init__(
            self,
            base_url: str,
            timeout: int | float | None = None,
            params: dict[str, str | int | float | bool | None] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            auth: tuple[str, str] | None = None,
            transport: httpx.AsyncHTTPTransport | None = None
        ):
        self._base_url = base_url
        self._timeout = timeout
        self._client = httpx.AsyncClient(
            base_url = base_url,
            timeout = timeout,
            params = params,
            headers = headers,
            cookies = cookies,
            auth = auth,
            transport = transport
        )
    
    async def render(self, text: str) -> Response[RenderResponse]:
        """Render markdown text to HTML."""
        response = await self._client.post(
            "/render",
            json = {
                "content": text
            }
        )
        return Response(
            response = response,
            model = RenderResponse
        )
