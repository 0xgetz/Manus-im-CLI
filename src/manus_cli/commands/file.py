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
    """Upload a file to the Manus platform for use in tasks."""
    state = ctx.obj
    client = state["client"]
    json_output = state["json"]
    api = FilesAPI(client)

    try:
        if path.stat().st_size == 0:
            print_error("Refusing to upload an empty file.")
            raise typer.Exit(code=2)

        filename = path.name
        # Create a file record, then stream to its validated presigned URL.
        res = api.upload(filename=filename)
        data = res.get("data", res)
        upload_url = data.get("upload_url")
        file_id = data.get("file_id") or data.get("id")

        if not upload_url or not file_id:
            print_error("Invalid upload response: missing upload_url or file_id.")
            raise typer.Exit(code=1)

        api.upload_file(upload_url, path)

        if json_output:
            print_json({"file_id": file_id, "filename": filename})
        else:
            print_success("File uploaded successfully!")
            print(f"File ID: {file_id}")
    except typer.Exit:
        raise
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(code=1) from exc
