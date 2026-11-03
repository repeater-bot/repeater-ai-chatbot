from ....runtime_container import RuntimeContainer
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field


@ToolsCaller.register
class WorkspaceEditTextRegex(ToolPackage):
    class Params(BaseModel):
        path: str = Field(..., description="The text file path to edit.")
        pattern: str = Field(..., description="Regular expression used to scan the text.")
        replacement: str = Field(..., description="re.sub replacement; supports backreferences like \\1.")
        count: int = Field(default=1, ge=0, description="Number of matches to replace; 0 means all.")
        ignore_case: bool = Field(default=False, description="Case-insensitive matching.")
        multiline: bool = Field(default=False, description="Make ^ and $ match line boundaries.")
        dotall: bool = Field(default=False, description="Make . match newlines.")
        encoding: str = Field(default="utf-8", description="Text encoding used to read and write the file.")

    name = "workspace_edit_text_regex"
    description = "Scan text with a regular expression, replace matches, and write the whole file back client-side."

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        data_client = global_runtime.data_client

        result = await data_client.edit_text_regex(
            path = args.path,
            pattern = args.pattern,
            replacement = args.replacement,
            count = args.count,
            ignore_case = args.ignore_case,
            multiline = args.multiline,
            dotall = args.dotall,
            text_encoding = args.encoding
        )
        return result.model_dump()
