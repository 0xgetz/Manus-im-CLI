"""Project commands."""

import typer
from rich.table import Table

from manus_cli.api.projects import ProjectsAPI
from manus_cli.output import console, print_error, print_json, print_success

app = typer.Typer(help="Project management commands.")


@app.command("create")
def project_create(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Project name."),
    instruction: str = typer.Option(None, "--instruction", help="Shared project instruction."),
):
    """Create a new project."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]
    api = ProjectsAPI(client)

    try:
        res = api.create(name=name, instruction=instruction)
        if json_output:
            print_json(res)
        else:
            print_success("Project created successfully!")
            print_json(res)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)


@app.command("list")
def project_list(
    ctx: typer.Context,
):
    """List all projects."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]
    api = ProjectsAPI(client)

    try:
        res = api.list_projects()
        if json_output:
            print_json(res)
        else:
            projects = res.get("data", [])
            table = Table(title="Projects")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Instruction", style="yellow")

            for p in projects:
                table.add_row(
                    str(p.get("id", "")),
                    str(p.get("name", "")),
                    str(p.get("instruction", ""))[:50],
                )
            console.print(table)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)
