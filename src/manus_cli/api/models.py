"""Pydantic data models for Manus API responses and requests."""

from typing import Any

from pydantic import BaseModel


class TaskCreateRequest(BaseModel):
    message: dict[str, Any]
    project_id: str | None = None
    structured_output_schema: dict[str, Any] | None = None


class TaskSendMessageRequest(BaseModel):
    task_id: str
    message: dict[str, Any]


class TaskConfirmActionRequest(BaseModel):
    task_id: str
    event_id: str
    input: dict[str, Any]


class ProjectCreateRequest(BaseModel):
    name: str
    instruction: str | None = None


class FileUploadRequest(BaseModel):
    filename: str
