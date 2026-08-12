<div align="center">
  <img src="../assets/logo.png" alt="Manus-im-CLI Logo" width="140" height="140" />
  <h1>Manus-im-CLI: Comprehensive API & Usage Guide</h1>
  <p><b>Advanced Technical Documentation for Developers and Power Users</b></p>
</div>

---

## 📋 Table of Contents

1. [Introduction & Architecture](#introduction--architecture)
2. [Authentication & Security](#authentication--security)
3. [Task Management & Lifecycle](#task-management--lifecycle)
4. [Projects & Instructions](#projects--instructions)
5. [File Uploads & Attachments](#file-uploads--attachments)
6. [Browser Control & Integration](#browser-control--integration)
7. [Advanced Scripting & Automation Examples](#advanced-scripting--automation-examples)
8. [Error Handling & Exit Codes](#error-handling--exit-codes)
9. [References](#references)

---

## 1. Introduction & Architecture

`Manus-im-CLI` is engineered with a clean, modular architecture that decouples the thin REST API client layer (`api/`) from the command-line interface (`commands/`) built on Typer and Rich [1] [2]. 

```
Manus-im-CLI/
├── src/manus_cli/
│   ├── api/
│   │   ├── client.py      # Core HTTPX client with rate limiting & retries
│   │   ├── tasks.py       # Task lifecycle endpoints
│   │   ├── projects.py    # Project management endpoints
│   │   ├── files.py       # File upload & browser clients
│   │   └── models.py      # Pydantic request/response schemas
│   ├── commands/          # CLI command modules (auth, task, project, file, browser, config)
│   ├── config.py          # Secure TOML config management (~/.config/manus)
│   ├── errors.py          # Custom exceptions and exit code mappings
│   └── output.py          # Rich formatting & key redaction utilities
```

---

## 2. Authentication & Security

All API communication requires an API key passed via the `x-manus-api-key` header [3].

### Storing Credentials
```bash
manus auth login --api-key manus_sk_live_...
```
*Security Note*: Credentials are saved in `~/.config/manus/config.toml` with strict `0600` file permissions. API keys are automatically redacted from all verbose/debug logging streams.

### Checking Authentication Status
```bash
manus auth whoami --json
```
**Example Response**:
```json
{
  "ok": true,
  "request_id": "req_auth_01",
  "data": {
    "balance": 2500,
    "currency": "credits"
  }
}
```

---

## 3. Task Management & Lifecycle

The Manus API v2 operates asynchronously [4]. Tasks go through distinct lifecycle states: `running`, `stopped`, `waiting`, and `error` [5].

### Creating a Task
```bash
manus task create "Perform competitive analysis on AI startups in Q2 2026" --watch
```
- **Stdin support**: You can pipe prompts directly from other commands:
  ```bash
  echo "Summarize system logs" | manust task create - --json
  ```

### Watching Task Events (`manus task watch`)
When executing with `--watch`, the CLI polls `/v2/task.listMessages` and handles events:
- **`assistant_message`**: Streams agent text output in real-time.
- **`waiting`**: Automatically detects `waiting_for_event_type`:
  - `messageAskUser`: Prompts for text reply and invokes `/v2/task.sendMessage`.
  - `needConnectMyBrowser`: Lists online browser clients and submits selection via `/v2/task.confirmAction`.
  - General Actions (e.g., `terminalExecute`): Prompts user for confirmation and submits `{ "accept": true }` [5].

### Manual Task Confirmation
```bash
manus task confirm tsk_123 evt_abc --accept --input '{"always_allow": true}'
```

---

## 4. Projects & Instructions

Projects allow you to group related tasks and apply shared instructions automatically [6].

### Creating a Project
```bash
manus project create "Financial Analytics" --instruction "Always output results in tabular format and verify data integrity."
```

### Listing Projects
```bash
manus project list --json
```

---

## 5. File Uploads & Attachments

Uploading files utilizes a secure two-step presigned URL mechanism [7]:
1. `POST /v2/file.upload` generates a presigned `upload_url` and a `file_id`.
2. `PUT` raw file bytes directly to `upload_url`.

### CLI Usage
```bash
manus file upload dataset.csv
# Output: File ID: file_abc987xyz
```
Pass the resulting `file_id` when creating a task:
```bash
manus task create "Analyze this dataset" --file file_abc987xyz
```

---

## 6. Browser Control & Integration

When tasks require local browser interaction, the agent triggers a `needConnectMyBrowser` event [5].

### Listing Online Browsers
```bash
manus browser list --json
```
**Example Response**:
```json
{
  "ok": true,
  "data": [
    {
      "client_id": "0e9ad711-8471-4fcc-a9de-8309f0f12c87",
      "status": "online"
    }
  ]
}
```

---

## 7. Advanced Scripting & Automation Examples

### Example 1: Automated Nightly Reporting Script (Python/Bash)
```bash
#!/usr/bin/env bash
set -e

# 1. Upload daily report template
FILE_ID=$(manus file upload /data/metrics.csv --json | jq -r '.file_id')

# 2. Create task non-interactively and capture output
TASK_RES=$(manus task create "Generate weekly executive summary from metrics" --file "$FILE_ID" --json)
TASK_ID=$(echo "$TASK_RES" | jq -r '.data.task_id')

echo "Started background task: $TASK_ID"

# 3. Watch task until completion
manus task watch "$TASK_ID"
```

### Example 2: Programmatic Python Client Integration
```python
from manus_cli.api.client import APIClient
from manus_cli.api.tasks import TasksAPI

client = APIClient(base_url="https://api.manus.ai", api_key="manus_sk_live_...")
tasks_api = TasksAPI(client)

# Create task
res = tasks_api.create(message={"content": [{"text": "Run data audit"}]})
task_id = res["data"]["task_id"]

# Poll messages
messages = tasks_api.list_messages(task_id=task_id, order="asc")
print(messages)
```

---

## 8. Error Handling & Exit Codes

`Manus-im-CLI` returns strict POSIX-compliant exit codes for reliable scripting and CI/CD integration:

| Exit Code | Error Category | Description |
| :--- | :--- | :--- |
| `0` | **Success** | Command executed successfully. |
| `1` | **General Error** | Runtime error, network failure, or unexpected API exception. |
| `2` | **Usage Error** | Invalid arguments, missing required parameters, or configuration lookup failure. |
| `3` | **Authentication Error** | Invalid API key, expired token, or lack of permissions (`permission_denied`) [3]. |
| `4` | **Rate Limit Error** | Too many requests (`rate_limited`) after exhausting exponential backoff retries [8]. |

---

## 9. References

- [1] Manus API v2 Introduction: `https://open.manus.ai/docs/v2/introduction`
- [2] Typer CLI Framework: `https://typer.tiangolo.com/`
- [3] Manus Authentication Guide: `https://open.manus.ai/docs/v2/authentication.md`
- [4] Manus Task Creation Guide: `https://open.manus.ai/docs/v2/task.create.md`
- [5] Manus Task Lifecycle & Confirmations: `https://open.manus.ai/docs/v2/task-lifecycle.md`
- [6] Manus Projects Documentation: `https://open.manus.ai/docs/v2/project.create.md`
- [7] Manus File Uploads: `https://open.manus.ai/docs/v2/file.upload.md`
- [8] Manus Rate Limits: `https://open.manus.ai/docs/v2/rate-limits.md`
