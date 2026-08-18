"""Config commands."""

import sys

import typer
from rich.prompt import Confirm

from manus_cli.config import (
    get_config_value,
    is_sensitive_config_key,
    load_config,
    set_config_value,
)
from manus_cli.output import print_error, print_json, print_success

app = typer.Typer(help="Configuration management commands.")


@app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key (e.g., base_url)."),
    value: str = typer.Argument(..., help="Configuration value."),
):
    """Set a configuration value."""
    set_config_value(key, value)
    rendered_value = "[REDACTED]" if is_sensitive_config_key(key) else value
    print_success(f"Set {key} = {rendered_value}")


@app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Configuration key."),
    show_secret: bool = typer.Option(
        False,
        "--show-secret",
        help="Display a sensitive value after explicit confirmation in an interactive terminal.",
    ),
):
    """Get a configuration value while redacting secrets by default."""
    val = get_config_value(key)
    if val is None:
        print_error(f"Configuration key '{key}' not found.")
        raise typer.Exit(code=2)

    if is_sensitive_config_key(key):
        if not show_secret:
            print("[REDACTED]")
            return
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            print_error("Refusing to reveal a secret outside an interactive terminal.")
            raise typer.Exit(code=2)
        if not Confirm.ask("Display this secret in the terminal?", default=False):
            raise typer.Exit(code=0)

    print(val)


@app.command("list")
def config_list():
    """List all configuration values while redacting sensitive values."""
    cfg = load_config()
    for key in cfg:
        if is_sensitive_config_key(key):
            cfg[key] = "[REDACTED]"
    print_json(cfg)
