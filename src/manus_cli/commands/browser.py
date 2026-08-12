"""Browser commands."""

import typer
from rich.table import Table

from manus_cli.api.files import BrowserAPI
from manus_cli.output import console, print_error, print_json

app = typer.Typer(help="Browser connection commands.")


@app.command("list")
def browser_list(
    ctx: typer.Context,
):
    """List online browser clients."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]
    api = BrowserAPI(client)

    try:
        res = api.online_list()
        if json_output:
            print_json(res)
        else:
            clients = res.get("data", [])
            table = Table(title="Online Browser Clients")
            table.add_column("Client ID", style="cyan")
            table.add_column("Status", style="green")

            for c in clients:
                table.add_row(
                    str(c.get("client_id", "")),
                    str(c.get("status", "online")),
                )
            console.print(table)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)
