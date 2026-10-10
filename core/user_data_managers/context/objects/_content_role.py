from enum import StrEnum

class ContentRole(StrEnum):
    """
    上下文角色
    """
    DEVELOPER = "developer"
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"