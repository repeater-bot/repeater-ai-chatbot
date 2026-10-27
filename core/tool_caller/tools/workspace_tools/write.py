import base64
from typing import Literal
from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field

class Content(BaseModel):
    type: Literal["content"] = Field(default="content", description="The type of the content.")
    content: str = Field(default=..., description="The content to write to the file.")
    encoding: str = Field(default="utf-8", description="The encoding to use when writing the file.")

class VarContent(BaseModel):
    type: Literal["var_content"] = Field(default="var_content", description="The type of the content.")
    var_name: str = Field(default=..., description="The name of the variable that holds the content.")
    base64_encode: bool = Field(default=False, description="Whether the variable holds base64 encoded text.")
    encoding: str | None = Field(default=None, description="The encoding used to turn the variable's text into bytes. Defaults to utf-8.")

@ToolsCaller.register
class WorkspaceWrite(ToolPackage):
    class Params(BaseModel):
        path: str = Field(default=..., description="The path of the file to write.")
        content: Content | VarContent = Field(default=..., description="The content to write to the file.")

    name = "workspace_write"
    description = "Write text to a workspace file, creating it if missing. Returns the number of bytes written."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        if isinstance(args.content, Content):
            size = await data_client.write_file(
                path = args.path,
                data = args.content.content.encode(
                    encoding = args.content.encoding
                )
            )
            return size
        elif isinstance(args.content, VarContent):
            data = await ToolsCaller.get_variable(
                user_id = runtime.user_id,
                variable_name = args.content.var_name
            )
            encoding = args.content.encoding or "utf-8"

            if isinstance(data, bytes):
                # Raw bytes as stored by `workspace_read` without an encoding, or
                # base64 encoded bytes when `base64_encode` is set.
                decoded_data = base64.b64decode(data, validate = True) \
                    if args.content.base64_encode else data
            elif isinstance(data, str):
                decoded_data = base64.b64decode(data.encode(encoding), validate = True) \
                    if args.content.base64_encode else data.encode(encoding)
            else:
                raise TypeError("Variable is not a string or bytes.")

            size = await data_client.write_file(
                path = args.path,
                data = decoded_data
            )
            return size
        else:
            raise TypeError("content must be of type Content or VarContent")