"""Tests for Manus API client using pytest and respx."""

import httpx
import pytest
import respx

from manus_cli.api.client import APIClient
from manus_cli.api.projects import ProjectsAPI
from manus_cli.api.tasks import TasksAPI
from manus_cli.errors import AuthError, RateLimitError


@pytest.fixture
def client():
    return APIClient(base_url="https://api.manus.ai", api_key="test-key")


@respx.mock
def test_task_create_success(client):
    respx.post("https://api.manus.ai/v2/task.create").mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "request_id": "req_123",
                "data": {"task_id": "tsk_abc", "task_url": "https://manus.im/task/tsk_abc"},
            },
        )
    )

    api = TasksAPI(client)
    res = api.create(message={"content": [{"text": "hello"}]})
    assert res["ok"] is True
    assert res["data"]["task_id"] == "tsk_abc"


@respx.mock
def test_api_error_handling(client):
    respx.get("https://api.manus.ai/v2/usage.availableCredits").mock(
        return_value=httpx.Response(
            401,
            json={
                "ok": False,
                "request_id": "req_401",
                "error": {"code": "unauthorized", "message": "Invalid API key"},
            },
        )
    )

    with pytest.raises(AuthError):
        client.get("/v2/usage.availableCredits")


@respx.mock
def test_rate_limit_error(client):
    respx.get("https://api.manus.ai/v2/task.list").mock(
        return_value=httpx.Response(
            429,
            headers={"Retry-After": "1"},
            json={
                "ok": False,
                "request_id": "req_429",
                "error": {"code": "rate_limited", "message": "Too many requests"},
            },
        )
    )

    with pytest.raises(RateLimitError):
        client.get("/v2/task.list")


@respx.mock
def test_project_create(client):
    respx.post("https://api.manus.ai/v2/project.create").mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "request_id": "req_proj",
                "data": {"id": "prj_123", "name": "Test Project"},
            },
        )
    )

    api = ProjectsAPI(client)
    res = api.create(name="Test Project")
    assert res["ok"] is True
    assert res["data"]["id"] == "prj_123"
