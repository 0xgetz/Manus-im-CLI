# Manus-im-CLI

[![CI](https://github.com/manus-ai/Manus-im-CLI/actions/workflows/ci.yml/badge.svg)](https://github.com/manus-ai/Manus-im-CLI/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

`Manus-im-CLI` is a full-featured, production-ready command-line interface client for the Manus AI agent platform (`https://manus.im`), wrapping the official Manus REST API v2 [1]. It allows developers and power users to create, monitor, interact with, and manage Manus AI agent tasks entirely from the Linux terminal.

## Getting an API Key

Before making API calls or logging in, you will need to create an API key:
1. Navigate to the [Manus API Integration settings](https://manus.im/app?show_settings=integrations&app_name=api) in the Manus webapp.
2. Click **Create API Key** and give it a descriptive name.
3. Copy the key immediately and store it securely [2].

## Installation

On Linux Ubuntu (20.04 / 22.04 / 24.04), ensure Python 3.10+ and `pip` are installed:

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
```

Install via `pipx` (recommended for isolated CLI tools):
```bash
pipx install .
```

Or install in editable/development mode via `pip`:
```bash
pip install -e .
```

## Quickstart

1. **Authenticate**:
   ```bash
   manus auth login
   ```
   *(Or set the `MANUS_API_KEY` environment variable).*

2. **Verify Auth**:
   ```bash
   manus auth whoami
   ```

3. **Create and Watch a Task**:
   ```bash
   manus task create "Analyze the latest AI trends" --watch
   ```

## Command Reference

### Authentication
- `manus auth login [--api-key KEY]` — Store API key securely in `~/.config/manus/config.toml` (permissions `0600`).
- `manus auth whoami` — Check current authentication and available credit balance.

### Tasks
- `manus task create "<prompt>" [--file PATH] [--project ID] [--connector NAME] [--skill NAME] [--json] [--watch]` — Create a new task. (Accepts prompt from stdin if omitted or `-`).
- `manus task list [--status running|stopped|waiting|error] [--project ID] [--limit N] [--json]` — List tasks.
- `manus task get <task_id> [--json]` — Retrieve task details and status.
- `manus task watch <task_id>` — Stream events and interactively respond to agent waiting prompts.
- `manus task send <task_id> "<message>"` — Send a follow-up message in a multi-turn conversation.
- `manus task confirm <task_id> <event_id> [--accept/--reject] [--input '<json>']` — Manually confirm or reject a pending action.

### Projects
- `manus project create <name> [--instruction TEXT]` — Create a new project with shared instructions.
- `manus project list [--json]` — List all projects.

### Files
- `manus file upload <path>` — Upload a file to the platform and receive a reusable `file_id`.

### Browser
- `manus browser list` — List online connected browser clients.

### Configuration
- `manus config set <key> <value>` — Set configuration value (e.g., `base_url`).
- `manus config get <key>` — Get configuration value.
- `manus config list` — List configuration values (redacting API keys).

## Global Options
- `--json` — Output machine-readable JSON for scripting and piping.
- `--verbose` / `--debug` — Print redacted raw HTTP request/response logs for troubleshooting.
- `--base-url <url>` — Override API base URL.
- `--no-color` — Disable colored Rich output.

## References
- [1] Manus API v2 Introduction: `https://open.manus.ai/docs/v2/introduction`
- [2] Manus Authentication Guide: `https://open.manus.ai/docs/v2/authentication.md`
