import typer

from .utils.parse_directory import parse_directory

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@app.command()
def main(dir: str, tree_only: bool = False):
    try:
        parse_directory(dir, tree_only)
    except OSError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
