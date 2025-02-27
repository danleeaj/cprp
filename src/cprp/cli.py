from .utils.parse_directory import parse_directory

import typer

app = typer.Typer()

@app.command()
def main(dir: str, tree_only: bool=False):
    parse_directory(dir, tree_only)

if __name__ == "__main__":
    app()