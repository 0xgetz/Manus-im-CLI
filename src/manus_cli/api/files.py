"""File-related and browser API methods."""

import pathlib
from typing import Any
from urllib.parse import urlsplit

import httpx

from manus_cli.api.client import APIClient


class FilesAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def upload(self, filename: str) -> dict[str, Any]:
        return self.client.post("/v2/file.upload", json_data={"filename": filename})

    @staticmethod
    def _validate_upload_url(upload_url: str) -> None:
        """Require a secure, absolute presigned URL before transferring file content."""
        parsed = urlsplit(upload_url)
        if parsed.scheme.lower() != "https" or not parsed.hostname:
            raise ValueError("Upload URL must be an absolute HTTPS URL.")
        if parsed.username or parsed.password:
            raise ValueError("Upload URL must not contain embedded credentials.")

    def upload_file(
        self,
        upload_url: str,
        path: pathlib.Path,
        content_type: str = "application/octet-stream",
    ) -> None:
        """Stream a local file to a validated presigned URL without buffering it in memory."""
        self._validate_upload_url(upload_url)
        headers = {"Content-Type": content_type}
        with (
            path.open("rb") as file_handle,
            httpx.Client(
                timeout=60.0,
                follow_redirects=False,
            ) as upload_client,
        ):
            response = upload_client.put(upload_url, content=file_handle, headers=headers)
        response.raise_for_status()


class BrowserAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def online_list(self) -> dict[str, Any]:
        return self.client.get("/v2/browser.onlineList")
