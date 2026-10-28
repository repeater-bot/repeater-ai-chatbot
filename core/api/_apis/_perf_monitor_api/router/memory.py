import psutil
from typing import Any
from .._router import perf_monitor_api

@perf_monitor_api.get("/memory")
async def monitor_memory():
    """
    Monitor Memory Usage
    """
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
