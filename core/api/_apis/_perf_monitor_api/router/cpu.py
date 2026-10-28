import psutil
from .._router import perf_monitor_api
from fastapi import Query
from .....auxiliary.monitor import async_cpu_percent

@perf_monitor_api.get("/cpu")
async def monitor_cpu(
    interval: float = Query(0.1, description="Interval between each measurement"),
    percpu: bool = Query(False, description="Whether to return per-core percentages")
):
    """
    Monitor CPU usage
    """
    result: dict[str, int | float | list[float] | None] = {
        "cores": psutil.cpu_count(),
        "logical_cores": psutil.cpu_count(logical=True),
        "percent": await async_cpu_percent(interval=interval, percpu=percpu)
    }
    return result
