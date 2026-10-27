from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class VariableExists(ToolPackage):
    class Params(BaseModel):
        variable_name: str = Field(..., description="The name of the variable to check.")

    name = "variable_exists"
    description = "Check if a variable exists."

    async def call(self, args: Params, runtime: RuntimePackage):
        exists = await ToolsCaller.variable_exists(
            user_id = runtime.user_id,
            variable_name = args.variable_name
        )

        if exists:
            return f"Variable '{args.variable_name}' already exists."
        else:
            return f"Variable '{args.variable_name}' does not exist."