class ToolCallerError(Exception):
    """
    Base exception of the tool calling framework.
    """


class PipeCloseException(ToolCallerError):
    """
    Raised when the other side of a pipe has been closed.
    """


class ToolContextError(ToolCallerError):
    """
    Raised when an interface is used outside of a tool call context,
    or when the context does not carry the required information.
    """


class ToolArgsError(ToolCallerError):
    """
    Raised when the raw arguments of a tool call can not be decoded or validated.

    The message of this exception is already user/model facing: it becomes the
    content of the tool response, the tool itself is never entered.
    """
