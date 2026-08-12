"""File-related and browser API methods."""

from typing import Any

import httpx

from manus_cli.api.client import APIClient


class FilesAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def upload(self, filename: str) -> dict[str, Any]:
        return self.client.post("/v2/file.upload", json_data={"filename": filename})

    def upload_bytes(
        self, upload_url: str, file_bytes: bytes, content_type: str = "application/octet-stream"
    ) -> None:
        """Upload raw file bytes via PUT to presigned upload_url."""
        headers = {"Content-Type": content_type}
        response = httpx.put(upload_url, content=file_bytes, headers=headers, timeout=60.0)
        response.raise_for_status()


class BrowserAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def online_list(self) -> dict[str, Any]:
        return self.client.get("/v2/browser.onlineList")
