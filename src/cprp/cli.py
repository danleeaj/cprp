import typer

from .utils.parse_directory import parse_directory

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@app.command()
def main(
    dir: str,
    tree_only: bool = False,
    no_follow_symlinks: bool = typer.Option(
        False, "--no-follow-symlinks", "-ns", help="Skip symbolic links inside the selected directory."
    ),
):
    try:
        parse_directory(dir, tree_only, follow_symlinks=not no_follow_symlinks)
    except OSError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
