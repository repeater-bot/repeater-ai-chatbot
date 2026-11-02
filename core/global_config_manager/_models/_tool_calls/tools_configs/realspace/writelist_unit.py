from pydantic import BaseModel, ConfigDict, Field

class RealspaceWritelistUnit(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    path: str
    read: bool = False
    read_text: bool = False
    write: bool = False
    append: bool = False
    truncate: bool = False
    touch: bool = False
    edit: bool = False
    edit_text: bool = False
    edit_text_by_char: bool = False
    edit_text_by_line: bool = False
    edit_text_regex: bool = False
    delete: bool = False
    exists: bool = False
    is_file: bool = False
    is_dir: bool = False
    glob: bool = False
    rematch: bool = False
    list: bool = False
    info: bool = False
    mkdir: bool = False
    move: bool = False
    copy_: bool = Field(default=False, alias="copy")
    get_url: bool = False
    hash: bool = False
    du: bool = False
    tree: bool = False
    copy_range: bool = False
