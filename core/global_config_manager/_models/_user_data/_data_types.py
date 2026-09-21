from pydantic import BaseModel, ConfigDict
from typing import TypeVar, Generic

T = TypeVar("T")

class DataTypes(BaseModel, Generic[T]):
    context: T | None = None
    prompt: T | None = None
    config: T | None = None
    program: T | None = None