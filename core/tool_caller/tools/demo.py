from ..framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel

@ToolsCaller.register
class Demo(ToolPackage):
    class Params(BaseModel):
        name: str
        data: str
        raise_error: bool = False
    
    name = "demo"
    enabled = False # Debug Only
    description = "Demo Tool"

    async def call(self, args: Params, runtime: RuntimePackage):
        if args.raise_error:
            raise ValueError("Demo Error")
        return f"Hello {args.name}, your data is {args.data}"
