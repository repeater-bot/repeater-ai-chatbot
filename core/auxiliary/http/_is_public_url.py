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