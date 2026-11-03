from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field

@ToolsCaller.register
class RealspaceEditText(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The real text file path to edit.")
        replacement: str = Field(..., description="Replacement text; empty string deletes the range.")
        start_char: int | None = Field(default=None, ge=0, description="Zero-based start character offset.")
        end_char: int | None = Field(default=None, ge=0, description="Zero-based end offset; null means start_char.")
        start_line: int | None = Field(default=None, ge=1, description="1-based start line.")
        start_column: int = Field(default=1, ge=1, description="1-based start column.")
        end_line: int | None = Field(default=None, description="1-based end line; null means start_line.")
        end_column: int | None = Field(default=None, description="1-based end column (exclusive); null means start_column.")
        encoding: str = Field(default="utf-8", description="Text encoding used to read and write the file.")

    name = "realspace_edit_text"
    description = "Edit text by character offsets, line/column, or both; both must resolve to the same range."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_edit_text")
        result = await data_client.edit_text(
            path=args.path, replacement=args.replacement,
            start_char=args.start_char, end_char=args.end_char,
            start_line=args.start_line, start_column=args.start_column,
            end_line=args.end_line, end_column=args.end_column,
            text_encoding=args.encoding
        )
        return result.model_dump()
