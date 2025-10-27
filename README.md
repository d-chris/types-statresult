# types-statresult

[![Python](https://img.shields.io/badge/python-3.10&#124;3.11&#124;3.12&#124;3.13&#124;3.14-blue?logoColor=yellow)](https://python.org)
[![Poetry](https://img.shields.io/badge/packaging-poetry==1.8.5-%233B82F6?logo=poetry)](https://python-poetry.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)

---

Extracts stub from mypy for `os.stat_result` to create a new protocol class to use as a type hint.
Refactor return types of attributes using a user-defined callback.

## Example

```python
from pathlib import Path

from types_statresult import refactor_statresult, black_fmt


def create_statresult(filename: str) -> int:
    """fetches os.stat_result and refactors its attribute types."""

    def refactor(attr: str, type: str) -> str:
        if attr.endswith("time"):
            return "TimeInt"
        elif attr == "st_size":
            return "ByteInt"

        return type

    code = refactor_statresult(refactor)

    code = black_fmt(code)

    code = "\n".join(
        [
            "import sys",
            "import typing",
            "",
            "from pathlibutil.types import ByteInt, TimeInt",
            "",
            "",
            code,
        ]
    )

    return Path(filename).write_text(code, encoding="utf-8")
```
