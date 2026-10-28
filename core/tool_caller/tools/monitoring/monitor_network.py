import psutil
import asyncio
from typing import Any
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class MonitorNetwork(ToolPackage):
    class Params(BaseModel):
        pass
    
    name = "monitor_network"
    description = "Gets network info on the server."

    def _call(self):
        net_io_counters = psutil.net_io_counters(pernic = True)

        process_net_io_dict: dict[str, list[dict[str, Any]]] = {}
        for name, net_io_counter in net_io_counters.items():
            net_io = process_net_io_dict.setdefault(name, [])
            net_io.append({
                "bytes_sent": net_io_counter.bytes_sent,
                "bytes_recv": net_io_counter.bytes_recv,
                "packets_sent": net_io_counter.packets_sent,
                "packets_recv": net_io_counter.packets_recv,
                "errin": net_io_counter.errin,
                "errout": net_io_counter.errout,
                "dropin": net_io_counter.dropin,
                "dropout": net_io_counter.dropout
            })
        
        net_connections = psutil.net_connections()
        net_connections_dict: dict[int | None, list[dict[str, Any]]] = {}
        for net_connection in net_connections:
            process_net_io = net_connections_dict.setdefault(net_connection.pid, [])
            process_net_io.append(
                {
                    "fd": net_connection.fd,
                    "family": net_connection.family.name,
                    "laddr_ip": net_connection.laddr.ip if net_connection.laddr else None,
                    "laddr_port": net_connection.laddr.port if net_connection.laddr else None,
                    "raddr_ip": net_connection.raddr.ip if net_connection.raddr else None,
                    "raddr_port": net_connection.raddr.port if net_connection.raddr else None,
                    "type": net_connection.type.name,
                    "status": net_connection.status
                }
            )

        result: dict[str, Any] = {
            "net_io_counters": process_net_io_dict,
            "net_connections": net_connections_dict
        }
        return result

    async def call(self, args: Params, runtime: RuntimePackage):
        # return asyncio.to_thread(
        #     self._call,
        # )
        return self._call()