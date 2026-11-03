from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ._client import get_realspace_client
from pydantic import BaseModel, Field

@ToolsCaller.register
class RealspaceEditTextByChar(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The real text file path to edit.")
        replacement: str = Field(..., description="Replacement text; empty string deletes the range.")
        start: int = Field(..., ge=0, description="Zero-based start character offset.")
        end: int | None = Field(default=None, ge=0, description="Zero-based end offset; null means start.")
        encoding: str = Field(default="utf-8", description="Text encoding used to read and write the file.")

    name = "realspace_edit_text_by_char"
    description = "Replace a text range by absolute character offsets, reading and writing the whole file."

    async def call(self, args: Params, runtime: RuntimePackage):
        data_client = get_realspace_client("realspace_edit_text_by_char")
        result = await data_client.edit_text_by_char(
            path=args.path, replacement=args.replacement, start=args.start,
            end=args.end, text_encoding=args.encoding
        )
        return result.model_dump()
