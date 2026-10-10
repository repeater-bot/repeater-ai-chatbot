from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .exceptions import ToolContextError

if TYPE_CHECKING:
    from fastapi import Request as FastAPI_Request
    from ...user_config_manager import UserConfigs


@dataclass
class ToolContext:
    """
    The per-call context of a tool call.

    `ToolsCaller` keeps one of those in a `ContextVar`, so a tool reaches the
    caller's identity through `ToolPackage.user_id` / `ToolPackage.user_configs`
    instead of the request-scoped constructor injection the old framework used.
    """

    user_id: str
    """The user that the tool call belongs to."""

    user_configs: UserConfigs | None = None
    """Configs of the user, if the caller provided them."""

    fastapi_request: FastAPI_Request | None = None
    """The request that started the whole generation loop, if there is one."""


_context: ContextVar[ToolContext | None] = ContextVar(
    "tool_caller_context",
    default = None
)


def get_context() -> ToolContext | None:
    """
    Get the context of the current tool call, or None when there is none.

    :return: The context of the current tool call.
    """
    return _context.get()


def set_context(context: ToolContext) -> Token[ToolContext | None]:
    """
    Enter a tool call context.

    :param context: The context to enter.
    :return: The token required to leave it again.
    """
    return _context.set(context)


def reset_context(token: Token[ToolContext | None]) -> None:
    """
    Leave the tool call context that the token belongs to.

    :param token: The token returned by `set_context`.
    """
    _context.reset(token)


def require_context() -> ToolContext:
    """
    Get the context of the current tool call.

    :return: The context of the current tool call.
    :raises ToolContextError: If the current task is not inside a tool call.
    """
    context = _context.get()
    if context is None:
        raise ToolContextError(
            "This interface can only be used inside a tool call."
        )
    return context
