"""Tests for secure API client and CLI behavior using pytest and respx."""

from pathlib import Path

import httpx
import pytest
import respx
from typer.testing import CliRunner

from manus_cli.__main__ import app
from manus_cli.api.client import APIClient
from manus_cli.api.files import FilesAPI
from manus_cli.api.projects import ProjectsAPI
from manus_cli.api.tasks import TasksAPI
from manus_cli.commands import task
from manus_cli.config import DEFAULT_BASE_URL, get_base_url, validate_base_url
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


@pytest.mark.parametrize(
    ("base_url", "allow_custom", "expected"),
    [
        (DEFAULT_BASE_URL, False, DEFAULT_BASE_URL),
        ("https://api.manus.ai/", False, DEFAULT_BASE_URL),
        ("https://gateway.example.test/v2", True, "https://gateway.example.test/v2"),
    ],
)
def test_validate_base_url_allows_secure_expected_hosts(base_url, allow_custom, expected):
    assert validate_base_url(base_url, allow_custom=allow_custom) == expected


@pytest.mark.parametrize(
    "base_url",
    [
        "http://api.manus.ai",
        "https://evil.example.test",
        "https://user:pass@api.manus.ai",
        "https://api.manus.ai/?unexpected=value",
    ],
)
def test_validate_base_url_rejects_untrusted_or_unsafe_values(base_url):
    with pytest.raises(ValueError):
        validate_base_url(base_url)


def test_get_base_url_uses_validated_default(monkeypatch):
    monkeypatch.delenv("MANUS_BASE_URL", raising=False)
    assert get_base_url() == DEFAULT_BASE_URL


def test_config_get_redacts_api_key_by_default(monkeypatch, tmp_path):
    from manus_cli import config as config_module

    config_file = tmp_path / "config.toml"
    config_file.write_text('api_key = "secret-value"\n', encoding="utf-8")
    monkeypatch.setattr(config_module, "CONFIG_FILE", config_file)

    runner = CliRunner()
    result = runner.invoke(app, ["config", "get", "api_key"])

    assert result.exit_code == 0
    assert result.output.strip() == "[REDACTED]"
    assert "secret-value" not in result.output


class _WatchAPI:
    def __init__(self):
        self.cursors: list[str | None] = []

    def list_messages(self, task_id, order, limit, starting_after=None):
        self.cursors.append(starting_after)
        if starting_after is None:
            return {
                "data": [
                    {
                        "event_id": "event-1",
                        "type": "assistant_message",
                        "assistant_message": {"content": "first response"},
                    }
                ]
            }
        return {
            "data": [
                {
                    "event_id": "event-2",
                    "type": "status_update",
                    "status_update": {"agent_status": "stopped"},
                }
            ]
        }


def test_watch_uses_event_cursor_and_detects_terminal_status(monkeypatch):
    api = _WatchAPI()
    monkeypatch.setattr(task.time, "sleep", lambda _: None)

    task._watch_task_loop(api, client=None, task_id="task-1", json_output=False)

    assert api.cursors == [None, "event-1"]


@respx.mock
def test_upload_file_uses_validated_https_url(tmp_path):
    path = Path(tmp_path / "sample.txt")
    path.write_text("content", encoding="utf-8")
    api = FilesAPI(APIClient(base_url=DEFAULT_BASE_URL))

    with pytest.raises(ValueError):
        api.upload_file("http://upload.example.test/object", path)


def test_manual_confirmation_defaults_to_reject(monkeypatch):
    confirmed_inputs: list[dict] = []

    def capture_confirmation(self, task_id, event_id, input_data):
        confirmed_inputs.append(input_data)
        return {"ok": True}

    monkeypatch.setattr(TasksAPI, "confirm_action", capture_confirmation)
    runner = CliRunner()
    result = runner.invoke(app, ["task", "confirm", "task-1", "event-1"])

    assert result.exit_code == 0
    assert confirmed_inputs == [{"accept": False}]
