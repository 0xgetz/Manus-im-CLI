"""Auth commands."""

import typer
from rich.prompt import Prompt

from manus_cli.api.client import APIClient
from manus_cli.config import get_base_url, set_config_value
from manus_cli.output import print_error, print_json, print_success

app = typer.Typer(help="Authentication commands.")


@app.command("login")
def login(
    api_key: str = typer.Option(None, "--api-key", help="API key to store."),
):
    """Interactively or via flag store Manus API key securely."""
    key = api_key
    if not key:
        key = Prompt.ask("Enter your Manus API key", password=True)

    if not key:
        print_error("API key cannot be empty.")
        raise typer.Exit(code=2)

    # Test API key by making a request
    base_url = get_base_url()
    client = APIClient(base_url=base_url, api_key=key)
    try:
        # Test against usage available credits or similar endpoint
        client.get("/v2/usage.availableCredits")
    except Exception as e:
        print_error(f"Failed to validate API key: {e}")
        raise typer.Exit(code=3)

    set_config_value("api_key", key)
    print_success("API key successfully saved to ~/.config/manus/config.toml (permissions 0600).")


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
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=3)
