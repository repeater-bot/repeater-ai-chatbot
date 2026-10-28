import psutil
import asyncio
from typing import overload, Literal, Protocol

class CPU_PERCENT(Protocol):
    @overload
    def __call__(
        self,
        interval: float | None = None,
        percpu: Literal[False] = False
    ) -> float:
        ...

    @overload
    def __call__(
        self,
        interval: float | None,
        percpu: Literal[True]
    ) -> list[float]:
        ...

    @overload
    def __call__(
        self,
        *,
        percpu: Literal[True]
    ) -> list[float]:
        ...

class PROCESS_CPU_PERCENT(Protocol):
    def __call__(
        self,
        interval: float | None = None
    ) -> float:
        ...

@overload
async def async_cpu_percent(
    interval: float | None = None,
    percpu: Literal[False] = False,
    cpu_percent_func: CPU_PERCENT = psutil.cpu_percent
) -> float:
    ...

@overload
async def async_cpu_percent(
    interval: float | None = None,
    percpu: Literal[True] = True,
    cpu_percent_func: CPU_PERCENT = psutil.cpu_percent
) -> list[float]:
    ...

async def async_cpu_percent(
    interval: float | None = None,
    percpu: bool = False,
    cpu_percent_func: CPU_PERCENT = psutil.cpu_percent
) -> float | list[float]:
    """Return the CPU usage percentage."""
    if interval is None:
        num_cpus = cpu_percent_func(percpu = percpu)
        return num_cpus
    elif isinstance(interval, float):
        first_num_cpus = cpu_percent_func(percpu = percpu)
        await asyncio.sleep(interval)
        second_num_cpus = cpu_percent_func(percpu = percpu)
        return second_num_cpus
    else:
        raise TypeError("interval must be a float or None")

async def async_process_cpu_percent(
    interval: float | None = None,
    cpu_percent_func: PROCESS_CPU_PERCENT = psutil.cpu_percent
) -> float:
    """Return the CPU usage percentage."""
    if interval is None:
        num_cpus = cpu_percent_func()
        return num_cpus
    elif isinstance(interval, float):
        first_num_cpus = cpu_percent_func()
        await asyncio.sleep(interval)
        second_num_cpus = cpu_percent_func()
        return second_num_cpus
    else:
        raise TypeError("interval must be a float or None")