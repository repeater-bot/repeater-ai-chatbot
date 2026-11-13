from typing import Any

from pydantic import BaseModel, Field


class CreateSQLiteRequest(BaseModel):
    path: str = Field(..., description="Filesystem path of the SQLite database to create or open.")


class ExecuteSQLiteRequest(BaseModel):
    sql: str = Field(..., description="One SQLite statement to execute.")
    params: list[Any] | dict[str, Any] | None = Field(
        default = None,
        description = "Optional positional or named parameters."
    )
