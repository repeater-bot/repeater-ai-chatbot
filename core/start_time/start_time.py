import time
from datetime import datetime

start_time_dt = datetime.now()
start_time = time.time()
start_time_ns = time.time_ns()
start_time_mono = time.monotonic()
start_time_mono_ns = time.monotonic_ns()
start_time_perf = time.perf_counter()
start_time_pref_ns = time.perf_counter_ns()
start_time_process = time.process_time()
start_time_process_ns = time.process_time_ns()

__all__ = [
    "start_time_dt",
    "start_time",
    "start_time_ns",
    "start_time_mono",
    "start_time_mono_ns",
    "start_time_perf",
    "start_time_pref_ns",
    "start_time_process",
    "start_time_process_ns",
]