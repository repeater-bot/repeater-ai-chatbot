from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class SetVariable(ToolPackage):
    class Params(BaseModel):
        variable_name: str = Field(..., description="The name of the variable to set.")
        encoding: str | None = Field(
            default = None,
            description = (
                "Encode the content into bytes with this encoding before storing it. "
                "Leave it null unless bytes are really needed: a bytes variable can "
                "not be dumped and forces `dump_variable` to fail for every variable."
            )
        )
        content: str = Field(..., description="The content to write to the variable.")

    name = "set_variable"
    description = "Write a variable to the user's variables."

    async def call(self, args: Params, runtime: RuntimePackage):
        if args.encoding is None:
            data = args.content
        else:
            data = args.content.encode(args.encoding)

        await ToolsCaller.set_variable(
            user_id = runtime.user_id,
            variable_name = args.variable_name,
            variable_value = data
        )

        return "Set variable finished."