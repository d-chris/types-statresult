from typer import Typer

app = Typer(add_completion=False)  # Disable --show-completion option


@app.command()
def main():
    return 0


if __name__ == "__main__":
    app()
