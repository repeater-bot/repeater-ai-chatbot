import re
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class VariablesList(ToolPackage):
    class Params(BaseModel):
        pattern: str = Field(default=r"^[\s\S]*$", description="The pattern to match variable names.")

    name = "variable_list"
    description = "List the user's variables and the type of every value."
    
    async def call(self, args: Params, runtime: RuntimePackage):
        variable_types = await ToolsCaller.variable_types(
            user_id = runtime.user_id
        )
        pattern = re.compile(args.pattern)

        return {
            name: variable_type
            for name, variable_type in variable_types
            if pattern.match(name)
        }