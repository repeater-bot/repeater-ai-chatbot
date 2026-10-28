import psutil
import asyncio
from typing import Any
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel

@ToolsCaller.register
class MonitorMemory(ToolPackage):
    class Params(BaseModel):
        pass
    
    name = "monitor_memory"
    description = "Gets memory usage on the server."

    def _call(self):
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        result: dict[str, Any] = {
            "virtual_memory": {
                "total_size": virtual_memory.total,
                "available_size": virtual_memory.available,
                "used_size": virtual_memory.used,
                "percent": virtual_memory.percent,
            },
            "swap_memory": {
                "total_size": swap_memory.total,
                "free_size": swap_memory.free,
                "used_size": swap_memory.used,
                "percent": swap_memory.percent
            }
        }
        return result

    async def call(self, args: Params, runtime: RuntimePackage):
        # return asyncio.to_thread(
        #     self._call
        # )
        return self._call()