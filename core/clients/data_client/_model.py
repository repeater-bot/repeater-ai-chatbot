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
