from dataclasses import dataclass
from pydantic import BaseModel
from ..output import Output

@dataclass
class ParamsPackage:
    args: BaseModel
    output: Output