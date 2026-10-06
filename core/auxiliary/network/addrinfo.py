import socket
import ipaddress
from typing import Self
from dataclasses import dataclass

@dataclass
class AddrInfo:
    family: socket.AddressFamily
    type: socket.SocketKind
    proto: int
    canonname: str
    sockaddr: tuple[str, int] | tuple[str, int, int, int] | tuple[int, bytes]
    
    @classmethod
    def from_addr(cls, addr: tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int] | tuple[str, int, int, int] | tuple[int, bytes]]) -> Self:
        family, type, proto, canonname, sockaddr = addr

        return cls(
            family = family,
            type = type,
            proto = proto,
            canonname = canonname,
            sockaddr = sockaddr
        )

    def to_sockaddr(self) -> tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int] | tuple[str, int, int, int] | tuple[int, bytes]]:
        return (
            self.family,
            self.type,
            self.proto,
            self.canonname,
            self.sockaddr
        )

    @property
    def ip_address(self) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
        return ipaddress.ip_address(self.sockaddr[0])

    @property
    def host(self) -> str:
        return str(self.ip_address)

    @property
    def port(self) -> int:
        if isinstance(self.port, int):
            return int(self.port)
        elif isinstance(self.port, bytes):
            # Port byteorder is big endian
            return int.from_bytes(self.port, "big")
        else:
            raise ValueError("Invalid port type")

    @property
    def flowinfo(self) -> int:
        if len(self.sockaddr) == 4:
            return self.sockaddr[2]
        else:
            raise ValueError("Not have this data.")

    @property
    def scope_id(self) -> int:
        if len(self.sockaddr) == 5:
            return self.sockaddr[4]
        else:
            raise ValueError("Not have this data.")

    @property
    def port_number(self) -> int:
        if isinstance(self.port, int):
            return self.port
        elif isinstance(self.port, bytes):
            return int.from_bytes(self.port, "big") # Port number is always big endian
        else:
            return 0
    
    @property
    def is_ipv6(self) -> bool:
        return self.family == socket.AF_INET6