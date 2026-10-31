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
