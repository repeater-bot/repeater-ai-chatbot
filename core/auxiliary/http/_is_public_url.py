import socket
import asyncio
from urllib.parse import urlsplit
from ipaddress import ip_address
from ..network import AddrInfo

async def is_public_url(url: str) -> bool:
    u = urlsplit(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise ValueError("Invalid HTTP URL")

    host = u.hostname
    port = u.port or (443 if u.scheme == "https" else 80)
    
    try:
        # ipaddress raises ValueError when the host is not an ip literal,
        # which means "this is a domain name, go resolve it below".
        return ip_address(host).is_global
    except ValueError:
            # is not an ip address
            # try to DNS resolve
            loop = asyncio.get_event_loop()
            addrs: list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int] | tuple[str, int, int, int] | tuple[int, bytes]]] = await loop.getaddrinfo(
                host,
                port,
                type = socket.SOCK_STREAM
            )
            # only public when every resolved address is global
            return all(
                AddrInfo.from_addr(addr).ip_address.is_global
                for addr in addrs
            )