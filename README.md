# types-statresult

[![Pyhton](https://img.shields.io/badge/python-3.14-blue?logoColor=yellow)](https://python.org)
[![Poetry](https://img.shields.io/badge/packaging-poetry-%233B82F6?logo=poetry)](https://python-poetry.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)

---

extract stub file for `os.stat_result` with create protocol with refined type hints.

## Example

```python
from pathlib import Path

from types_statresult import refactor_statresult, black_fmt


def create_statresult(filename: str) -> int:

    def refactor(name: str, type: str) -> str:
        if name.endswith("time"):
            return "TimeInt"
        elif name == "st_size":
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
