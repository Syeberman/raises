import pytest

from raises import UndeclaredException, raises


def test_basic():
    """Allows the declared exceptions to pass through; other non-fatal exceptions are re-raised as
    UndeclaredException."""

    @raises(TypeError)
    def raise_declared():
        raise TypeError

    pytest.raises(TypeError, raise_declared)

    @raises(TypeError)
    def raise_undeclared():
        raise ValueError

    excinfo = pytest.raises(UndeclaredException, raise_undeclared)
    assert excinfo.match("^unexpected ValueError from raise_undeclared$")
    assert type(excinfo.value.__cause__) is ValueError

    @raises(TypeError)
    def raise_nothing():
        return "success"

    assert raise_nothing() == "success"


def test_multiple_exceptions():
    """Multiple exceptions can be declared."""

    def multi_exceptions(exc: type[BaseException]):
        @raises(TypeError, ValueError)
        def multi_exceptions_inner():
            raise exc

        return multi_exceptions_inner

    pytest.raises(TypeError, multi_exceptions(TypeError))

    pytest.raises(ValueError, multi_exceptions(ValueError))

    excinfo = pytest.raises(UndeclaredException, multi_exceptions(LookupError))
    assert type(excinfo.value.__cause__) is LookupError


def test_no_exceptions():
    """If no exceptions are declared, all non-fatal exceptions are re-raised as
    UndeclaredException."""

    def exceptions_empty(exc: type[BaseException] | BaseException):
        @raises()
        def exceptions_empty_inner():
            raise exc

        return exceptions_empty_inner

    # pytest.raises(BaseException) will catch everything, so check the type.
    excinfo = pytest.raises(BaseException, exceptions_empty(BaseException))
    assert excinfo.type is BaseException

    pytest.raises(KeyboardInterrupt, exceptions_empty(KeyboardInterrupt))

    excinfo = pytest.raises(
        UndeclaredException, exceptions_empty(UndeclaredException("", ""))
    )
    assert excinfo.value.__cause__ is None

    excinfo = pytest.raises(UndeclaredException, exceptions_empty(Exception))
    assert type(excinfo.value.__cause__) is Exception

    excinfo = pytest.raises(UndeclaredException, exceptions_empty(ValueError))
    assert type(excinfo.value.__cause__) is ValueError


def test_raise_fatal_exception():
    """All fatal exceptions pass through."""

    def non_Exception(exc: type[BaseException] | BaseException):
        @raises(TypeError)
        def non_Exception_inner():
            raise exc

        return non_Exception_inner

    # pytest.raises(BaseException) will catch everything, so check the type.
    excinfo = pytest.raises(BaseException, non_Exception(BaseException))
    assert excinfo.type is BaseException

    pytest.raises(KeyboardInterrupt, non_Exception(KeyboardInterrupt))

    excinfo = pytest.raises(
        UndeclaredException, non_Exception(UndeclaredException("", ""))
    )
    assert excinfo.value.__cause__ is None


# FIXME Wrap a method.


def test_parentheses_required():
    """Give a helpful error if the parentheses are missing."""

    re_match = r"^parentheses are required: @raises\(\)$"
    with pytest.raises(TypeError, match=re_match):
        @raises  # type: ignore # fmt: skip
        def no_parentheses():  # type: ignore
            pass  # pragma: no cover


def test_only_Exception_subclasses():
    """Only proper subclasses of Exception can be declared; Exception, and the fatal exceptions, are
    not allowed."""

    re_match = r"^all exceptions must be Exception subclasses$"
    with pytest.raises(TypeError, match=re_match):
        raises(BaseException)  # type: ignore
    with pytest.raises(TypeError, match=re_match):
        raises(ValueError, KeyboardInterrupt)  # type: ignore
    with pytest.raises(TypeError, match=re_match):
        raises(UndeclaredException, ValueError)  # type: ignore
    with pytest.raises(TypeError, match=re_match):
        raises(Exception)


def test_wraps():
    """Ensures functools.wraps is applied properly."""

    @raises(TypeError)
    def original_function(original_parameter: int) -> int:
        "Original docstring."
        return original_parameter  # pragma: no cover

    assert original_function.__module__ == "test_raises"
    assert original_function.__name__ == "original_function"
    assert original_function.__qualname__ == "test_wraps.<locals>.original_function"
    assert original_function.__annotations__ == {
        "original_parameter": int,
        "return": int,
    }
    assert original_function.__doc__ == "Original docstring."
