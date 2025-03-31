"""raises - Declared, unchecked exceptions"""

__version__ = "0.1"


import functools
from typing import Callable, ParamSpec, TypeVar


_P = ParamSpec("_P")
_R = TypeVar("_R")


# Get a reference to the built-in function type.
# fmt: off
def _a_function(): pass   # pragma: no cover
_function = type(_a_function)
# fmt: on


class UndeclaredException(BaseException):
    def __init__(self) -> None:
        super().__init__("undeclared exception raised")


def raises(
    *exceptions: type[Exception],
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    if exceptions and isinstance(exceptions[0], _function):
        raise TypeError("parentheses are required: @raises()")
    for exception in exceptions:
        if exception is Exception or not issubclass(exception, Exception):  # type: ignore
            raise TypeError("all exceptions must be Exception subclasses")

    def raises_decorator(function: Callable[_P, _R]) -> Callable[_P, _R]:
        @functools.wraps(function)
        def raises_function(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            try:
                return function(*args, **kwargs)
            except exceptions:
                raise
            except Exception as exc:
                raise UndeclaredException() from exc

        return raises_function

    return raises_decorator
