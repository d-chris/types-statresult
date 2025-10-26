# types-statresult

## Example

```python
from types_statresult import refactor_statresult, black_fmt
from pathlib import Path


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
