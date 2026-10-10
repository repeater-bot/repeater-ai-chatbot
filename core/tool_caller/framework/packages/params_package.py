from dataclasses import dataclass
from typing import TypeVar, Generic
from pydantic import BaseModel
from ..output import Output

T = TypeVar("T", bound=BaseModel)

@dataclass
class ParamsPackage(Generic[T]):
    args: T
    output: Output