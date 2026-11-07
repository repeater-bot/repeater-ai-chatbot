from enum import StrEnum


class ShellLevel(StrEnum):
    OFF = "off"
    READ_ONLY = "read_only"
    PATH_WRITE = "path_write"
    FULL_ACCESS = "full_access"
