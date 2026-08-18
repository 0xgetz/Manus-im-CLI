"""Auth commands."""

import typer
from rich.prompt import Prompt

from manus_cli.api.client import APIClient
from manus_cli.config import get_base_url, set_config_value
from manus_cli.output import print_error, print_json, print_success

app = typer.Typer(help="Authentication commands.")


@app.command("login")
def login(
    ctx: typer.Context,
    api_key: str | None = typer.Option(None, "--api-key", help="API key to store."),
    base_url: str | None = typer.Option(None, "--base-url", help="Override API base URL."),
    allow_custom_base_url: bool = typer.Option(
        False,
        "--allow-custom-base-url",
        help="Allow a trusted custom HTTPS API endpoint to receive API credentials.",
    ),
):
    """Interactively or via flag store Manus API key securely."""
    key = api_key
    if not key:
        key = Prompt.ask("Enter your Manus API key", password=True)

    if not key:
        print_error("API key cannot be empty.")
        raise typer.Exit(code=2)

    try:
        if base_url:
            resolved_base_url = get_base_url(base_url, allow_custom=allow_custom_base_url)
        else:
            resolved_base_url = ctx.obj["client"].base_url
    except (KeyError, ValueError) as exc:
        print_error(str(exc))
        raise typer.Exit(code=2) from exc

    # Test API key only after validating the destination endpoint.
    client = APIClient(base_url=resolved_base_url, api_key=key)
    try:
        client.get("/v2/usage.availableCredits")
    except Exception as exc:
        print_error(f"Failed to validate API key: {exc}")
        raise typer.Exit(code=3) from exc

    set_config_value("api_key", key)
    print_success("API key saved to ~/.config/manus/config.toml (permissions 0600).")


@app.command("whoami")
def whoami(
    ctx: typer.Context,
):
    """Check current authentication status and available credits."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]

    try:
        res = client.get("/v2/usage.availableCredits")
        if json_output:
            print_json(res)
        else:
            print_success("Authenticated successfully!")
            print_json(res)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(code=3) from exc
