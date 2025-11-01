# types-statresult

[![Python](https://img.shields.io/badge/python-3.10&#124;3.11&#124;3.12&#124;3.13&#124;3.14-blue?logoColor=yellow)](https://python.org)
[![GitHub release](https://img.shields.io/github/v/release/d-chris/types-statresult?logo=github&label=release)](https://github.com/d-chris/types-statresult/releases)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/d-chris/types-statresult/tox.yml?logo=pytest&label=pytest)](https://github.com/d-chris/types-statresult/actions/workflows/tox.yml)
[![Poetry](https://img.shields.io/badge/packaging-poetry==1.8.5-%233B82F6?logo=poetry)](https://python-poetry.org/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/d-chris/types-statresult/main.svg)](https://results.pre-commit.ci/latest/github/d-chris/types-statresult/main)
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
