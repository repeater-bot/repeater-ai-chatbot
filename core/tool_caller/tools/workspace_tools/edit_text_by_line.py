from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceEditTextByLine(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The text file path to edit.")
        replacement: str = Field(..., description="Replacement text; empty string deletes the range.")
        start_line: int = Field(default=1, ge=1, description="1-based start line.")
        start_column: int = Field(default=1, ge=1, description="1-based start column.")
        end_line: int | None = Field(default=None, description="1-based end line; null means start_line.")
        end_column: int | None = Field(default=None, description="1-based end column (exclusive); null means start_column.")
        encoding: str = Field(default="utf-8", description="Text encoding used to read and write the file.")

    name = "workspace_edit_text_by_line"
    description = "Replace a text range by line/column, reading and writing the whole file client-side."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        result = await data_client.edit_text_by_line(
            path = args.path,
            replacement = args.replacement,
            start_line = args.start_line,
            start_column = args.start_column,
            end_line = args.end_line,
            end_column = args.end_column,
            text_encoding = args.encoding
        )
        return result.model_dump()
