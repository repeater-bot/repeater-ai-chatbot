from __future__ import annotations

from environs import Env
from typing import ClassVar
from .runtime import RepeaterRuntime

class RuntimeContainer:
    _instance: ClassVar[RuntimeContainer] | None = None
    _objects: ClassVar[RepeaterRuntime] | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    @classmethod
    def init_runtime(cls, env: Env) -> RepeaterRuntime:
        cls._objects = RepeaterRuntime(env)
        return cls._objects
    
    @classmethod
    def get_runtime(cls) -> RepeaterRuntime:
        if cls._objects is None:
            raise RuntimeError("GlobalObjects not initialized")
        return cls._objects