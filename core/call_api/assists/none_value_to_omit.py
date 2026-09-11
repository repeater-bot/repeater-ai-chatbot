from typing import overload, TypeVar, Callable, Any
from openai import Omit, omit

T_Value = TypeVar("T_Value")
T_Return = TypeVar("T_Return")

@overload
def none_to_omit(
    value: None,
    get_value: Callable[[T_Value], T_Return] | None = None
) -> Omit:
    ...

@overload
def none_to_omit(
    value: T_Value | None,
    get_value: None = None
) -> T_Value:
    ...

@overload
def none_to_omit(
    value: T_Value | None,
    get_value: Callable[[T_Value], T_Return] | None = None
) -> T_Return:
    ...

def none_to_omit(
    value: T_Value | None,
    get_value: Callable[[T_Value], T_Return] | None = None
) -> T_Value | T_Return | Omit:
    if value is None:
        return omit

    if get_value is not None:
        return get_value(value)
    else:
        return value
