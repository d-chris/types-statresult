import pytest

from types_statresult.statresult import get_code, get_statresult, refactor_statresult


@pytest.fixture()
def stub():
    return """\
import sys

class dummy:
    def __init__(self, *args): ...

@final
class stat_result:

    if sys.version_info >= (3, 10):
        __match_args__: Final = ("st_mode", "st_ino", "st_dev", "st_nlink", "st_uid")

    @property
    @deprecated("message")
    def st_ctime(self) -> int: ...
    @property
    def st_size(self) -> int: ...
    @property
    def st_mtime(self) -> int: ...
"""


def test_get_code():
    code = get_code()

    assert isinstance(code, str)
    assert "class stat_result" in code


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


def test_refactor_statresult():

    def refactor(name, type):
        return type

    code = refactor_statresult(refactor)

    assert isinstance(code, str)
    assert "class stat_result(typing.Protocol):" in code
