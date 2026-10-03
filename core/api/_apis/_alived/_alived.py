import time
from .._root import root_router
from fastapi.responses import PlainTextResponse
from ....start_time import start_time

@root_router.get("/alived", tags=["alived_check"])
def alived():
    return PlainTextResponse("OK")

@root_router.get("/alived/time", tags=["alived_check"])
@root_router.get("/alived/time/s", tags=["alived_check"])
def alived_time():
    now = time.perf_counter_ns()
    return PlainTextResponse(
        content = str((now - start_time) / 1e9)
    )

@root_router.get("/alived/time/ms", tags=["alived_check"])
def alived_time_ms():
    now = time.perf_counter_ns()
    return PlainTextResponse(
        content = str((now - start_time) / 1e6)
    )

@root_router.get("/alived/time/us", tags=["alived_check"])
def alived_time_us():
    now = time.perf_counter_ns()
    return PlainTextResponse(
        content = str((now - start_time) / 1e3)
    )

@root_router.get("/alived/time/ns", tags=["alived_check"])
def alived_time_ns():
    now = time.perf_counter_ns()
    return PlainTextResponse(
        content = str(now - start_time)
    )