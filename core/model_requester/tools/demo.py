from ...context import ToolCallPackage
from .._caller import ModelRequester
from pydantic import BaseModel

@ModelRequester.reg_global_package
class Demo(ToolCallPackage):
    class Params(BaseModel):
        name: str
        data: str
        raise_error: bool = False
    
    name = "demo"
    enabled = False # Debug Only
    description = "Demo Tool"

    def call(self, args: Params):
        if args.raise_error:
            raise ValueError("Demo Error")
        return f"Hello {args.name}, your data is {args.data}"