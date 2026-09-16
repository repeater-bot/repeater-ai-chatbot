import httpx
from ....auxiliary.http import get_ssl_context

horizontal_client = httpx.AsyncClient(
    verify = get_ssl_context(),
)