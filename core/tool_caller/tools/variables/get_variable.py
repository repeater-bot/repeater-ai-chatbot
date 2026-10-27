import orjson
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

@ToolsCaller.register
class GetVariable(ToolPackage):
    class Params(BaseModel):
        variable_name: str = Field(..., description="The name of the variable to read.")
        encoding: str | None = Field(
            default = None,
            description = (
                "Decode a variable that holds bytes with this encoding. "
                "Only valid for bytes values; leave it null to read anything else."
            )
        )

    name = "get_variable"
    description = "Read a variable from the user's variables."

    async def call(self, args: Params, runtime: RuntimePackage):
        try:
            data = await ToolsCaller.get_variable(
                runtime.user_id,
                args.variable_name
            )
        except KeyError:
            return f"{args.variable_name} is not found."

        if args.encoding is not None:
            if not isinstance(data, bytes):
                raise ValueError(f"Cannot decode {args.variable_name}({type(data).__name__}).")
            return data.decode(args.encoding)

        # str and bytes keep the repr form: the `b'...'` literal is how a caller
        # sees that the value holds bytes, which can never be dumped. Every
        # other value is returned as JSON so a model can parse it directly.
        if isinstance(data, (str, bytes)):
            return repr(data)
        try:
            return orjson.dumps(data).decode(encoding = "utf-8")
        except orjson.JSONEncodeError:
            return repr(data)