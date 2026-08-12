"""File commands."""

import pathlib

import typer

from manus_cli.api.files import FilesAPI
from manus_cli.output import print_error, print_json, print_success

app = typer.Typer(help="File upload and management commands.")


@app.command("upload")
def file_upload(
    ctx: typer.Context,
    path: pathlib.Path = typer.Argument(
        ..., help="Path to file to upload.", exists=True, dir_okay=False
    ),
):
    """Upload a file to Manus platform for use in tasks."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]
    api = FilesAPI(client)

    try:
        filename = path.name
        # 1. Create file record and get upload_url
        res = api.upload(filename=filename)
        data = res.get("data", res)
        upload_url = data.get("upload_url")
        file_id = data.get("file_id") or data.get("id")

        if not upload_url or not file_id:
            print_error(f"Invalid upload response: {res}")
            raise typer.Exit(code=1)

        # 2. Read file bytes and PUT to upload_url
        file_bytes = path.read_bytes()
        api.upload_bytes(upload_url, file_bytes)

        if json_output:
            print_json({"file_id": file_id, "filename": filename})
        else:
            print_success("File uploaded successfully!")
            print(f"File ID: {file_id}")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)
