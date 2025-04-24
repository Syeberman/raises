"""raises - No unexpected exceptions"""

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
    """Fatal exception indicating that a function decorated with `@raises()` raised an unexpected
    exception. The original exception is available in __cause__."""

    def __init__(self, function_name: str, exception_name: str, /) -> None:
        super().__init__(f"unexpected {exception_name} from {function_name}")


def raises(
    *exceptions: type[Exception],
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """`raises` is a function decorator that ensures only the declared non-fatal exceptions are
    raised. Any unexpected non-fatal exception is re-raised as a fatal exception.

    >>> @raises(TypeError)
    ... def my_function(key):
    ...     return int({'key': None}[key])  # FIXME Better example

    >>> my_function('key')
    Traceback (most recent call last):
    ...
    TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'

    >>> my_function('not_key')
    Traceback (most recent call last):
    ...
    raises.UndeclaredException: unexpected KeyError from my_function

    "Non-fatal exceptions" refers to `Exception` and its subclasses. Non-fatal exceptions are
    possibly caught and handled in the normal operation of the program, whereas fatal exceptions
    should usually terminate the program. See [PEP 760](https://peps.python.org/pep-0760/) for more
    details on this distinction.

    Multiple exceptions can be declared. Declared exceptions must be subclasses of Exception, but
    not Exception itself. Only undeclared non-fatal exceptions are re-raised as UndeclaredException.
    """
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
                raise UndeclaredException(
                    function.__name__, type(exc).__name__
                ) from exc

        return raises_function

    return raises_decorator
