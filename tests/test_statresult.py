import pytest

from types_statresult.statresult import (
    get_code,
    get_statresult,
    refactor_statresult,
    black_fmt,
)


@pytest.fixture(scope="session")
def stub():
    return """\
import sys

class dummy:
    def __init__(self, *args): ...

@final
class stat_result:

    my_var = 123

    if sys.version_info >= (3, 10):
        __match_args__: Final = ("st_mode", "st_ino", "st_dev", "st_nlink", "st_uid")

        @property
        def st_mtime(self) -> int: ...
    else:
        def st_birthtime(self) -> int: ...

    @property
    @deprecated("message")
    def st_ctime(self) -> int: ...
    @property
    def st_size(self) -> int: ...

    def my_method(self) -> None: ...
"""


def test_get_code():
    code = get_code()

    assert isinstance(code, str)
    assert "class stat_result" in code


def test_get_code_raises(mocker):

    mocker.patch("types_statresult.statresult.find_spec", return_value=None)

    with pytest.raises(FileNotFoundError):
        get_code()


@pytest.mark.parametrize(
    "decorator",
    [
        "@final",
        "@deprecated",
        "__match_args__",
        "class dummy",
    ],
)
def test_removed_decorators(stub, decorator):

    assert decorator in stub

    code = get_statresult(stub)

    assert decorator not in code


def test_statresult_protocol(stub):
    code = get_statresult(stub)

    assert isinstance(code, str)
    assert "class stat_result(typing.Protocol):" in code


def test_statresult_raises():

    with pytest.raises(ValueError):
        get_statresult("class NotStatResult:\n    pass")


def test_refactor_statresult(mocker, stub):

    def refactor(name, type):
        return "str"

    assert "-> str:" not in stub
    assert "-> int:" in stub

    mocker.patch(
        "types_statresult.statresult.get_code",
        return_value=stub,
    )

    code = refactor_statresult(refactor)

    assert "-> str:" in black_fmt(code)
