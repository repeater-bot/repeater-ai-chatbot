import psutil
from typing import Any
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field
from ....auxiliary.monitor import async_cpu_percent

@ToolsCaller.register
class MonitorCPU(ToolPackage):
    class Params(BaseModel):
        interval: float = Field(0.1, description="Interval between each CPU usage check.")
        percpu: bool = Field(False, description="Returns CPU usage per process.")
    
    name = "monitor_cpu"
    description = "Gets server CPU performance."

    async def _call(self, args: Params):
        result: dict[str, Any] = {
            "cores": psutil.cpu_count(),
            "logical_cores": psutil.cpu_count(logical=True),
            "percent": await async_cpu_percent(interval=args.interval, percpu=args.percpu)
        }
        return result

    async def call(self, args: Params, runtime: RuntimePackage):
        return await self._call(args)