"""Task-related API methods."""

from typing import Any

from manus_cli.api.client import APIClient


class TasksAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create(
        self,
        message: dict[str, Any],
        project_id: str | None = None,
        structured_output_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"message": message}
        if project_id:
            payload["project_id"] = project_id
        if structured_output_schema:
            payload["structured_output_schema"] = structured_output_schema
        return self.client.post("/v2/task.create", json_data=payload)

    def list_messages(
        self,
        task_id: str,
        order: str = "desc",
        limit: int = 10,
        starting_after: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"task_id": task_id, "order": order, "limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        return self.client.get("/v2/task.listMessages", params=params)

    def send_message(self, task_id: str, message: dict[str, Any]) -> dict[str, Any]:
        payload = {"task_id": task_id, "message": message}
        return self.client.post("/v2/task.sendMessage", json_data=payload)

    def confirm_action(
        self, task_id: str, event_id: str, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        payload = {"task_id": task_id, "event_id": event_id, "input": input_data}
        return self.client.post("/v2/task.confirmAction", json_data=payload)

    def list_tasks(
        self,
        status: list[str] | None = None,
        project_id: str | None = None,
        limit: int = 100,
        after: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        if project_id:
            params["project_id"] = project_id
        if after:
            params["after"] = after
        return self.client.get("/v2/task.list", params=params)

    def detail(self, task_id: str) -> dict[str, Any]:
        return self.client.get("/v2/task.detail", params={"task_id": task_id})

    def stop(self, task_id: str) -> dict[str, Any]:
        return self.client.post("/v2/task.stop", json_data={"task_id": task_id})

    def delete(self, task_id: str) -> dict[str, Any]:
        return self.client.post("/v2/task.delete", json_data={"task_id": task_id})
