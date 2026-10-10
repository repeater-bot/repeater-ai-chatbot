from dataclasses import dataclass
from typing import (
    Generic,
    Self,
    TypeVar,
)

from pydantic import BaseModel

from ..output import Output

T = TypeVar("T", bound=BaseModel)


@dataclass
class ParamsPackage(Generic[T]):
    """
    Everything a single tool call carries.

    It is handed to `ToolPackage.handler` / `ToolPackage.call` by the framework
    and is the only place where per-call state lives, since tool instances
    themselves are process wide singletons.
    """

    user_id: str
    """The user that the tool call belongs to."""

    tool_call_id: str
    """The id of the tool call, as the model sent it."""

    args: T
    """The parsed arguments of the tool call."""

    output: Output
    """The output channel of this tool call."""

    loop_times: int | None = None
    """The current generation round, if the caller tracks them."""

    max_loop_times: int | None = None
    """The generation round limit, if the caller tracks them."""

    @classmethod
    def build(
        cls,
        user_id: str,
        args: T,
        tool_call_id: str = "",
        output: Output | None = None,
        loop_times: int | None = None,
        max_loop_times: int | None = None,
    ) -> Self:
        """
        Build a params package, filling in the parts a direct caller does not care about.

        :param user_id: The user that the tool call belongs to.
        :param args: The parsed arguments of the tool call.
        :param tool_call_id: The id of the tool call.
        :param output: The output channel to use, a new one is created when omitted.
        :param loop_times: The current generation round.
        :param max_loop_times: The generation round limit.
        :return: The params package.
        """
        return cls(
            user_id = user_id,
            tool_call_id = tool_call_id,
            args = args,
            output = output if output is not None else Output(),
            loop_times = loop_times,
            max_loop_times = max_loop_times,
        )
