import httpx
import socket
import asyncio
import ipaddress
from ..network import AddrInfo

class PublicIPOnlyTransport(httpx.AsyncHTTPTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        url = request.url
        host = url.host
        port = url.port

        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private:
                raise httpx.TransportError("Private network requests are not allowed")
        except ValueError:
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
                if addr_info.ip_address.is_private:
                    raise httpx.TransportError("Private network requests are not allowed")
        
        response: httpx.Response = await super().handle_async_request(request)
        return response