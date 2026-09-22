import httpx
from ....auxiliary.http import get_ssl_context

dispatch_trigger_client = httpx.AsyncClient(
    verify = get_ssl_context(),
)