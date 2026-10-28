import psutil
import asyncio
from typing import Any
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class MonitorDisk(ToolPackage):
    class Params(BaseModel):
        all_partitions: bool = Field(False, description="Show all partitions, including those that are not mounted.")
    
    name = "monitor_disk"
    description = "Gets disk info on the server."

    def _partition(self, all_partitions: bool):
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
        

    def _call(self, args: Params):
        result: dict[str, Any] = {
            "partitions": [
                partition for partition in self._partition(all_partitions = args.all_partitions)
            ]
        }
        return result

    async def call(self, args: Params, runtime: RuntimePackage):
        # return asyncio.to_thread(
        #     self._call,
        #     args
        # )
        return self._call(args)