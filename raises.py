"""raises - Declared, unchecked exceptions"""

__version__ = "0.1"


import functools
from typing import Callable, Iterable, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


class UncaughtException(BaseException): pass # FIXME


def raises(exceptions: Iterable[type[Exception]] = ()) -> Callable[[Callable[P, R]], Callable[P, R]]:
    exceptions = tuple(exceptions)
    for exception in exceptions:
        if exception is Exception or not issubclass(exception, Exception):
            raise TypeError("raises only allows Exception subclasses") # FIXME

    def raises_decorator(function: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(function)
        def raises_function(*args:P.args, **kwargs:P.kwargs) -> R:
            try:
                return function(*args, **kwargs)
            except exceptions:
                raise
            except Exception as e:
                raise UncaughtException(e)

        return raises_function

    return raises_decorator
