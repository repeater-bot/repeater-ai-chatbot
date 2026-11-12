from pydantic import BaseModel, ConfigDict


class FileInfo(BaseModel):
    """Metadata returned by ``GET /operations/info/{path}``."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    size: int
    st_mtime: float
    st_mtime_ns: int
    st_atime: float
    st_atime_ns: int
    st_mode: str


class DeleteResult(BaseModel):
    """Result returned by ``DELETE /operations/delete/{path}``."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    deleted_files: int
    deleted_dirs: int


class MoveResult(BaseModel):
    """Result returned by ``POST /operations/move/{path}``."""

    source: str
    destination: str


class CopyResult(MoveResult):
    """Result returned by ``POST /operations/copy/{path}``."""

    copied_files: int
    copied_dirs: int


class HashResult(BaseModel):
    """Result returned by ``GET /operations/hash/{path}``."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    algorithm: str
    digest: str
    size: int


class DiskUsage(BaseModel):
    """Result returned by ``GET /operations/du/{path}``."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    path: str
    size: int
    files: int
    dirs: int


class CopyRangeResult(BaseModel):
    """Result returned by ``POST /operations/copy_range/{path}``."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    source: str
    destination: str
    size: int


class TextLine(BaseModel):
    """One decoded line, with character offsets into the whole text."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    number: int
    start: int
    end: int
    raw_end: int
    text: str
    ending: str


class TextMetadata(BaseModel):
    """Client-side metadata for a decoded text file."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    path: str
    encoding: str
    byte_size: int
    char_count: int
    line_count: int
    newline: str
    st_mtime: float
    st_mode: str


class TextFile(BaseModel):
    """Result of ``DataClient.get_text_file``."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    content: str
    numbered_content: str
    lines: list[TextLine]
    metadata: TextMetadata


class TextEditResult(BaseModel):
    """Result of a client-side character-range edit."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    path: str
    mode: str
    start_char: int
    end_char: int
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    replaced_chars: int
    char_count: int
    line_count: int
    size: int
    metadata: TextMetadata


class TextRegexMatch(BaseModel):
    """One regex match, with character and line/column positions."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    start: int
    end: int
    text: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int


class TextRegexEditResult(BaseModel):
    """Result of a client-side regex edit."""

    model_config = ConfigDict(
        validate_assignment = True
    )

    path: str
    pattern: str
    replacement: str
    requested_count: int
    replaced: int
    matches: list[TextRegexMatch]
    char_count: int
    line_count: int
    size: int
    metadata: TextMetadata


class SQLiteAccess(BaseModel):
    model_config = ConfigDict(validate_assignment = True)

    id: str
    path: str


class SQLiteExecuteResult(BaseModel):
    model_config = ConfigDict(validate_assignment = True)

    columns: list[str]
    rows: list[list]
    rowcount: int
    lastrowid: int | None = None


class SQLiteDatabaseInfo(BaseModel):
    model_config = ConfigDict(validate_assignment = True)

    id: str
    path: str
    opened_at: str
