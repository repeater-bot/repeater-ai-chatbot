import psutil
from typing import Any
from fastapi import Query
from .._router import perf_monitor_api

def partition(all_partitions: bool):
    partitions = psutil.disk_partitions(all=all_partitions)
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        yield {
            "device": partition.device,
            "mountpoint": partition.mountpoint,
            "fstype": partition.fstype,
            "opts": partition.opts,
            "usage": {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            }
        }
        
@perf_monitor_api.get("/disk")
async def monitor_disk(
    all_partitions: bool = Query(False)
):
    result: dict[str, Any] = {
        "partitions": [
            part for part in partition(all_partitions = all_partitions)
        ]
    }
    return result