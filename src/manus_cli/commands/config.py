"""Config commands."""

import typer

from manus_cli.config import get_config_value, load_config, set_config_value
from manus_cli.output import print_error, print_json, print_success

app = typer.Typer(help="Configuration management commands.")


@app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key (e.g., base_url)."),
    value: str = typer.Argument(..., help="Configuration value."),
):
    """Set a configuration value."""
    set_config_value(key, value)
    print_success(f"Set {key} = {value}")


@app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Configuration key."),
):
    """Get a configuration value."""
    val = get_config_value(key)
    if val is not None:
        print(val)
    else:
        print_error(f"Configuration key '{key}' not found.")
        raise typer.Exit(code=2)


@app.command("list")
def config_list():
    """List all configuration values (redacting api_key)."""
    cfg = load_config()
    if "api_key" in cfg:
        cfg["api_key"] = "[REDACTED]"
    print_json(cfg)
