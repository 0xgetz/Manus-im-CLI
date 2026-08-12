"""Output formatting using Rich and JSON."""

import json
from typing import Any

from rich.console import Console

console = Console()
err_console = Console(stderr=True)


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    console.print(json.dumps(data, indent=2, ensure_ascii=False))


def print_error(message: str, request_id: str | None = None) -> None:
    """Print error message to stderr."""
    msg = f"[bold red]Error:[/bold red] {message}"
    if request_id:
        msg += f" (request_id: {request_id})"
    err_console.print(msg)


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[bold green]Success:[/bold green] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[bold blue]Info:[/bold blue] {message}")


def redact_api_key(text: str, api_key: str | None = None) -> str:
    """Redact API key from text/logs."""
    if not text:
        return text
    if api_key and len(api_key) > 4:
        text = text.replace(api_key, "[REDACTED]")
    # Also look for x-manus-api-key header or Bearer tokens
    import re

    text = re.sub(r'(x-manus-api-key:\s*)[^\s"]+', r"\1[REDACTED]", text, flags=re.IGNORECASE)
    text = re.sub(r'(Bearer\s+)[^\s"]+', r"\1[REDACTED]", text, flags=re.IGNORECASE)
    return text
