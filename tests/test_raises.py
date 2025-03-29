import pytest
from raises import UndeclaredException, raises


# FIXME Assert we are wrapping correctly.
#


def test_basic():
    @raises(TypeError)
    def raise_expected():
        raise TypeError

    pytest.raises(TypeError, raise_expected)

    @raises(TypeError)
    def raise_unexpected():
        raise ValueError

    excinfo = pytest.raises(UndeclaredException, raise_unexpected)
    assert excinfo.match("^undeclared exception raised$")
    assert type(excinfo.value.__cause__) is ValueError

    @raises(TypeError)
    def nothing_raised():
        return "success"

    assert nothing_raised() == "success"


def test_raise_non_Exception():
    def non_Exception(exc: type[BaseException]):
        @raises(TypeError)
        def non_Exception_inner():
            raise exc

        return non_Exception_inner

    # BaseException matches everything, so be specific.
    excinfo = pytest.raises(BaseException, non_Exception(BaseException))
    assert excinfo.type is BaseException

    pytest.raises(KeyboardInterrupt, non_Exception(KeyboardInterrupt))

    excinfo = pytest.raises(UndeclaredException, non_Exception(UndeclaredException))
    assert excinfo.value.__cause__ is None


def test_exceptions_empty():
    def exceptions_empty(exc: type[BaseException]):
        @raises()
        def exceptions_empty_inner():
            raise exc

        return exceptions_empty_inner

    # BaseException matches everything, so be specific.
    excinfo = pytest.raises(BaseException, exceptions_empty(BaseException))
    assert excinfo.type is BaseException

    pytest.raises(KeyboardInterrupt, exceptions_empty(KeyboardInterrupt))

    excinfo = pytest.raises(UndeclaredException, exceptions_empty(UndeclaredException))
    assert excinfo.value.__cause__ is None

    excinfo = pytest.raises(UndeclaredException, exceptions_empty(Exception))
    assert type(excinfo.value.__cause__) is Exception

    excinfo = pytest.raises(UndeclaredException, exceptions_empty(ValueError))
    assert type(excinfo.value.__cause__) is ValueError


def test_parentheses_required():
    re_match = r"^parentheses are required: @raises\(\)$"
    with pytest.raises(TypeError, match=re_match):
        @raises  # type: ignore # fmt: skip
        def no_parentheses():  # type: ignore
            pass  # pragma: no cover


def test_only_Exception_subclasses():
    re_match = r"^all exceptions must be Exception subclasses$"
    with pytest.raises(TypeError, match=re_match):
        raises(BaseException)  # type: ignore
    with pytest.raises(TypeError, match=re_match):
        raises(KeyboardInterrupt)  # type: ignore
    with pytest.raises(TypeError, match=re_match):
        raises(UndeclaredException)  # type: ignore
    with pytest.raises(TypeError, match=re_match):
        raises(Exception)
