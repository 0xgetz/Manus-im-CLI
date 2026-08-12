"""Project-related API methods."""

from typing import Any

from manus_cli.api.client import APIClient


class ProjectsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create(self, name: str, instruction: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": name}
        if instruction:
            payload["instruction"] = instruction
        return self.client.post("/v2/project.create", json_data=payload)

    def list_projects(self) -> dict[str, Any]:
        return self.client.get("/v2/project.list")
