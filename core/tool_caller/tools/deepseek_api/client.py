import httpx
from ....auxiliary.http import get_ssl_context

deepseek_api_client = httpx.AsyncClient(
    verify = get_ssl_context(),
)
