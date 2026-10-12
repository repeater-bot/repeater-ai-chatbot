from typing import (
    Any,
    Protocol,
    Type,
    TypeVar,
)

T = TypeVar("T")

class New(Protocol[T]):
    def __call__(self, cls: Type[T], *args: Any, **kwargs: Any) -> T:
        ...