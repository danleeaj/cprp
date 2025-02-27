if __name__ == "__main__":
    try:
        from .cli import app
    except ImportError:
        from cprp.cli import app
    app()