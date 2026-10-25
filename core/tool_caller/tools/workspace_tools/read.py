import base64
from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field
from typing import Literal

class Content(BaseModel):
    type: Literal["content"] = Field(default="content", description="The type of the content.")
    base64_encode: bool = Field(default=False, description="Whether to base64 encode the content.")
    encoding: str = Field(default="utf-8", description="The encoding used to decode the file content.")

class VarContent(BaseModel):
    type: Literal["var_content"] = Field(default="var_content", description="The type of the content.")
    var_name: str = Field(default=..., description="The name of the variable that receives the content.")
    encoding: str | None = Field(default=None, description="The encoding used to decode the file content. When null the variable holds the raw bytes.")
    base64_encode: bool = Field(default=False, description="Whether to base64 encode the content.")

@ToolsCaller.register
class WorkspaceRead(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The path of the file to read.")
        content: Content | VarContent = Field(default=..., description="How to return the content: inline, or into a variable.")

    name = "workspace_read"
    description = "Read a file from the workspace."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        result = await data_client.get_file(args.path)
        if isinstance(args.content, Content):
            if args.content.base64_encode:
                encoded_result = base64.b64encode(result).decode(args.content.encoding)
            else:
                encoded_result = result.decode(args.content.encoding)
            return encoded_result
        elif isinstance(args.content, VarContent):
            # `base64_encode` used to be ignored when no encoding was given, which
            # silently stored raw bytes instead of the requested base64 text.
            if args.content.base64_encode:
                encoded_result = base64.b64encode(result).decode(
                    encoding = args.content.encoding or "utf-8"
                )
            elif args.content.encoding:
                encoded_result = result.decode(args.content.encoding)
            else:
                encoded_result = result
            
            await ToolsCaller.set_variable(
                runtime.user_id,
                args.content.var_name,
                encoded_result
            )
            return f"Written to variable {args.content.var_name}({encoded_result.__class__.__name__})."