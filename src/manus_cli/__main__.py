"""Main entry point for Manus CLI."""

import typer

from manus_cli.api.client import APIClient
from manus_cli.commands import auth, browser, config, file, project, task
from manus_cli.config import get_api_key, get_base_url

app = typer.Typer(
    help="Manus AI CLI - Official command-line interface for the Manus AI platform.",
    add_completion=True,
)

# Register sub-apps
app.add_typer(auth.app, name="auth")
app.add_typer(task.app, name="task")
app.add_typer(project.app, name="project")
app.add_typer(file.app, name="file")
app.add_typer(config.app, name="config")
app.add_typer(browser.app, name="browser")


@app.callback()
def main(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Output machine-readable JSON."),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress non-essential output."),
    verbose: bool = typer.Option(
        False, "--verbose", "--debug", help="Enable verbose debug logging."
    ),
    base_url: str = typer.Option(None, "--base-url", help="Override API base URL."),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output."),
):
    """Global options and client context initialization."""
    resolved_base_url = get_base_url(base_url)
    api_key = get_api_key()

    client = APIClient(base_url=resolved_base_url, api_key=api_key, debug=verbose)

    ctx.obj = {
        "client": client,
        "json": json_output,
        "quiet": quiet,
        "verbose": verbose,
    }


if __name__ == "__main__":
    app()
