from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class VariablesList(ToolPackage):
    class Params(BaseModel):
        pass

    name = "variable_list"
    description = "List the user's variables and the type of every value."

    async def call(self, args: Params, runtime: RuntimePackage):
        variable_types = await ToolsCaller.variable_types(
            user_id = runtime.user_id
        )

        return [
            {
                "name": name,
                "type": variable_type
            }
            for name, variable_type in variable_types
        ]