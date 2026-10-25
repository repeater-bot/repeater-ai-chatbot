from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class RemoveVariable(ToolPackage):
    class Params(BaseModel):
        variable_name: str = Field(..., description="The name of the variable to remove.")

    name = "remove_variable"
    description = "Remove a variable from the user's variables."

    async def call(self, args: Params, runtime: RuntimePackage):
        await ToolsCaller.remove_variable(
            user_id = runtime.user_id,
            variable_name = args.variable_name
        )

        return "Variable removed."