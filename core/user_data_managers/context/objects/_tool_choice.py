from enum import StrEnum

class ToolChoice(StrEnum):
    """
    Enum for tool choices
    """
    NONE = "none"
    AUTO = "auto"
    REQUIRED = "required"
    FORCE = "force"