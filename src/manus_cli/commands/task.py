"""Task commands and polling/watch loop."""

import json
import sys
import time

import typer
from rich.prompt import Confirm, Prompt
from rich.table import Table

from manus_cli.api.files import BrowserAPI
from manus_cli.api.tasks import TasksAPI
from manus_cli.output import console, print_error, print_json, print_success

app = typer.Typer(help="Task management and execution commands.")


def _build_message_payload(
    prompt: str, files: list[str], connectors: list[str], skills: list[str]
) -> dict:
    content: list[dict] = []
    if prompt:
        content.append({"text": prompt})
    for f in files:
        content.append({"file_id": f})

    msg: dict = {"content": content}
    if connectors:
        msg["connectors"] = connectors
    if skills:
        msg["enable_skills"] = skills
    return msg


@app.command("create")
def task_create(
    ctx: typer.Context,
    prompt: str | None = typer.Argument(
        None, help="Task prompt (use '-' or omit to read from stdin)."
    ),
    file_ids: list[str] = typer.Option(
        [], "--file", help="File ID to attach (can be specified multiple times)."
    ),
    project_id: str | None = typer.Option(None, "--project", help="Project ID."),
    connector: list[str] = typer.Option([], "--connector", help="Connector name/ID."),
    skill: list[str] = typer.Option([], "--skill", help="Skill name/ID to enable."),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON."),
    watch: bool = typer.Option(
        False, "--watch", help="Watch task progress immediately after creation."
    ),
):
    """Create a new task."""
    state = ctx.obj
    client = state["client"]
    api = TasksAPI(client)

    # Read prompt from stdin if needed
    if not prompt or prompt == "-":
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        else:
            prompt = Prompt.ask("Enter task prompt")

    if not prompt:
        print_error("Task prompt cannot be empty.")
        raise typer.Exit(code=2)

    message = _build_message_payload(prompt, file_ids, connector, skill)

    try:
        res = api.create(message=message, project_id=project_id)
        data = res.get("data", res)
        task_id = data.get("task_id") or data.get("id")

        if json_output and not watch:
            print_json(res)
        else:
            print_success("Task created successfully!")
            print(f"Task ID: {task_id}")
            print(f"Task URL: {data.get('task_url', '')}")

        if watch and task_id:
            # Delegate to task_watch command logic
            _watch_task_loop(api, client, task_id, json_output)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)


@app.command("list")
def task_list(
    ctx: typer.Context,
    status: list[str] = typer.Option(
        [], "--status", help="Filter by status (running, stopped, waiting, error)."
    ),
    project_id: str | None = typer.Option(None, "--project", help="Filter by project ID."),
    limit: int = typer.Option(100, "--limit", help="Limit number of results (1-1000)."),
):
    """List tasks."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]
    api = TasksAPI(client)

    try:
        res = api.list_tasks(status=status if status else None, project_id=project_id, limit=limit)
        if json_output:
            print_json(res)
        else:
            tasks = res.get("data", [])
            table = Table(title="Tasks")
            table.add_column("Task ID", style="cyan")
            table.add_column("Title", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Created", style="dim")

            for t in tasks:
                table.add_row(
                    str(t.get("task_id") or t.get("id", "")),
                    str(t.get("task_title") or t.get("title", "")),
                    str(t.get("agent_status") or t.get("status", "")),
                    str(t.get("created_at", "")),
                )
            console.print(table)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)


@app.command("get")
def task_get(
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="Task ID."),
):
    """Get task details and status."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]
    api = TasksAPI(client)

    try:
        res = api.detail(task_id)
        if json_output:
            print_json(res)
        else:
            print_json(res)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)


@app.command("watch")
def task_watch(
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="Task ID to watch."),
):
    """Watch task events, stream messages, and handle waiting confirmations interactively."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]
    api = TasksAPI(client)
    _watch_task_loop(api, client, task_id, json_output)


def _watch_task_loop(api: TasksAPI, client, task_id: str, json_output: bool):
    """Watch task events using a cursor so that new messages are not skipped."""
    print(f"Watching task {task_id} (Ctrl+C to exit watch mode)...")
    seen_event_ids: set[str] = set()
    starting_after: str | None = None
    latest_status: str | None = None

    while True:
        try:
            res = api.list_messages(
                task_id=task_id,
                order="asc",
                limit=50,
                starting_after=starting_after,
            )
            events = res.get("data", [])
            waiting_details = None

            for ev in events:
                ev_id = ev.get("event_id") or ev.get("id")
                if ev_id and ev_id in seen_event_ids:
                    continue
                if ev_id:
                    seen_event_ids.add(ev_id)
                    starting_after = ev_id

                ev_type = ev.get("type")
                if ev_type == "status_update":
                    status_update = ev.get("status_update", {})
                    latest_status = status_update.get("agent_status", latest_status)
                    if latest_status == "waiting":
                        waiting_details = status_update.get("status_detail", {})
                elif ev_type == "assistant_message":
                    content = ev.get("assistant_message", {}).get("content", "")
                    if json_output:
                        print(json.dumps(ev))
                    else:
                        console.print(f"\n[bold cyan]Assistant:[/bold cyan] {content}")
                elif ev_type == "error_message":
                    err_msg = ev.get("error_message", {}).get("message", "Unknown error")
                    if json_output:
                        print(json.dumps(ev))
                    else:
                        console.print(f"\n[bold red]Agent Error:[/bold red] {err_msg}")

            if latest_status == "stopped":
                print("\n[+] Task completed successfully.")
                break
            if latest_status == "error":
                print("\n[!] Task failed with error status.")
                break
            if latest_status == "waiting" and waiting_details:
                _handle_waiting_event(api, client, task_id, waiting_details)

            # Use a short delay even after handling an event to avoid a busy polling loop.
            time.sleep(3.0)

        except KeyboardInterrupt:
            print("\nExiting watch mode.")
            break
        except Exception as exc:
            print_error(str(exc))
            time.sleep(5.0)


def _handle_waiting_event(api: TasksAPI, client, task_id: str, detail: dict):
    event_id = detail.get("waiting_for_event_id")
    event_type = detail.get("waiting_for_event_type")
    description = detail.get("waiting_description", "Agent is waiting for input/confirmation.")
    schema = detail.get("confirm_input_schema", {})

    console.print(f"\n[bold yellow][WAITING] {event_type}: {description}[/bold yellow]")

    if not event_id:
        print_error("Waiting event is missing an event ID; refusing to confirm it.")
        return

    if event_type == "messageAskUser":
        # Reply with task.sendMessage
        reply = Prompt.ask("Enter your reply to the agent")
        api.send_message(task_id, {"content": [{"text": reply}]})
        print("Reply sent.")
    elif event_type == "needConnectMyBrowser":
        # List online browsers
        browser_api = BrowserAPI(client)
        b_res = browser_api.online_list()
        clients = b_res.get("data", [])
        if not clients:
            console.print(
                "[red]No online browser clients found. Skipping or connect browser extension.[/red]"
            )
            action = Confirm.ask("Skip browser connection?")
            if action:
                api.confirm_action(task_id, event_id, {"action": "skip"})
            return

        console.print("Available browser clients:")
        for idx, bc in enumerate(clients):
            console.print(f"[{idx}] Client ID: {bc.get('client_id')}")

        choice = Prompt.ask("Select browser index or enter client_id, or 'skip'", default="0")
        if choice.lower() == "skip":
            api.confirm_action(task_id, event_id, {"action": "skip"})
        else:
            client_id = choice
            if choice.isdigit():
                index = int(choice)
                if index >= len(clients):
                    print_error("Browser index is out of range; no selection was sent.")
                    return
                client_id = clients[index].get("client_id")
            if not client_id:
                print_error("Selected browser does not include a client ID; no selection was sent.")
                return
            api.confirm_action(task_id, event_id, {"action": "select", "client_id": client_id})
        print("Browser selection sent.")
    else:
        # General confirm action
        accept = Confirm.ask("Do you want to accept/confirm this action?", default=False)
        input_payload: dict = {"accept": accept}

        # Check schema properties for extra fields like always_allow or global_allow
        properties = schema.get("properties", {})
        if "always_allow" in properties and accept:
            always = Confirm.ask("Set always_allow?", default=False)
            input_payload["always_allow"] = always
        if "global_allow" in properties and accept:
            global_all = Confirm.ask("Set global_allow?", default=False)
            input_payload["global_allow"] = global_all

        api.confirm_action(task_id, event_id, input_payload)
        print("Confirmation sent.")


@app.command("send")
def task_send(
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="Task ID."),
    message_text: str = typer.Argument(..., help="Message text to send."),
):
    """Send a follow-up message to an existing task."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]
    api = TasksAPI(client)

    try:
        res = api.send_message(task_id, {"content": [{"text": message_text}]})
        if json_output:
            print_json(res)
        else:
            print_success("Message sent successfully!")
            print_json(res)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)


@app.command("confirm")
def task_confirm(
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="Task ID."),
    event_id: str = typer.Argument(..., help="Event ID to confirm."),
    accept: bool = typer.Option(False, "--accept/--reject", help="Accept or reject the action."),
    input_json: str | None = typer.Option(None, "--input", help="Custom JSON input string."),
):
    """Manually confirm or reject a pending task action."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]
    api = TasksAPI(client)

    try:
        input_data = json.loads(input_json) if input_json else {"accept": accept}
        res = api.confirm_action(task_id, event_id, input_data)
        if json_output:
            print_json(res)
        else:
            print_success("Action confirmation sent successfully!")
            print_json(res)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)
