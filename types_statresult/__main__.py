from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from typer import Argument, Exit, Typer

from types_statresult.statresult import create_ostypes

app = Typer(add_completion=False)  # Disable --show-completion option


@app.command()
def main(
    filename: Path = Argument(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        help="Path to the output file",
    )
):
    """Generate os.stat_result stub file with refined types."""

    bytes = create_ostypes(filename)

    raise Exit(code=0 if bytes > 0 else 1)


if __name__ == "__main__":
    app()
