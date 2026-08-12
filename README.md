<div align="center">
  <img src="assets/logo.png" alt="Manus-im-CLI Logo" width="160" height="160" />
  <h1>Manus-im-CLI</h1>
  <p><b>Your Autonomous AI Agent Platform in the Terminal</b></p>
  
  <p>
    <a href="README.md">English</a> |
    <a href="docs/README.zh.md">中文</a> |
    <a href="docs/README.es.md">Español</a> |
    <a href="docs/README.fr.md">Français</a> |
    <a href="docs/README.ja.md">日本語</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License" />
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/version-0.1.0-orange.svg" alt="Version" />
  </p>
</div>

---

## 🌟 Overview

`Manus-im-CLI` is a full-featured, production-ready command-line interface client for the **Manus AI agent platform** (`https://manus.im`), wrapping the official Manus REST API v2 [1]. It empowers developers, engineers, and power users to create, monitor, interact with, and manage autonomous AI agent tasks seamlessly from the Linux terminal.

<div align="center">
  <img src="assets/demo.png" alt="Manus-im-CLI Terminal Demo" width="90%" />
  <p><em>Interactive Task Creation and Real-Time Event Streaming with Manus-im-CLI</em></p>
</div>

---

## 🔑 Getting an API Key

Before making API calls or authenticating, you need to create an API key from your account:
1. Navigate to the [Manus API Integration settings](https://manus.im/app?show_settings=integrations&app_name=api) in the Manus webapp.
2. Click **Create API Key** and assign a descriptive name (e.g., `cli-production`) [2].
3. Copy the key immediately and store it securely [2].

---

## 📦 Installation

On Linux Ubuntu (20.04 / 22.04 / 24.04), ensure Python 3.10+ and `pip` are installed:

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
```

### Option A: Install via `pipx` (Recommended)
```bash
pipx install .
```

### Option B: Install in Editable Mode via `pip`
```bash
pip install -e .
```

### Option C: Android Installation via Termux
You can run `Manus-im-CLI` directly on your Android device using [Termux](https://termux.dev/). Follow these steps:

1. **Install Termux** from [F-Droid](https://f-Droid.org/packages/com.termux/) (Recommended) or Google Play Store.
2. **Update packages and install Python & Git**:
   ```bash
   pkg update && pkg upgrade -y
   pkg install python git -y
   ```
3. **Clone the repository**:
   ```bash
   git clone https://github.com/0xgetz/Manus-im-CLI.git
   cd Manus-im-CLI
   ```
4. **Install dependencies and the CLI**:
   ```bash
   pip install --upgrade pip
   pip install .
   ```
5. **Verify installation**:
   ```bash
   manus --help
   ```

---

## 🚀 Quickstart

1. **Authenticate Securely**:
   ```bash
   manus auth login
   ```
   *(Alternatively, set the `MANUS_API_KEY` environment variable).*

2. **Verify Authentication**:
   ```bash
   manus auth whoami
   ```

3. **Create and Watch an Autonomous Task**:
   ```bash
   manus task create "Analyze Q2 tech market trends and compile key insights" --watch
   ```

---

## 📋 Command Reference

### Authentication (`manus auth`)
| Command | Description |
| :--- | :--- |
| `manus auth login [--api-key KEY]` | Interactively or via flag store your Manus API key securely in `~/.config/manus/config.toml` (permissions `0600`) [3]. |
| `manus auth whoami` | Verify current authentication status and retrieve available platform credits [3]. |

### Tasks (`manus task`)
| Command | Description |
| :--- | :--- |
| `manus task create "<prompt>" [options]` | Create a new task. Supports `--file`, `--project`, `--connector`, `--skill`, `--json`, and `--watch` flags. Accepts stdin when prompt is `-` or omitted [3]. |
| `manus task list [options]` | List tasks with filtering by `--status` (`running`, `stopped`, `waiting`, `error`), `--project`, and `--limit` [3]. |
| `manus task get <task_id>` | Retrieve detailed metadata and status for a specific task [3]. |
| `manus task watch <task_id>` | Stream events in real-time, show spinners, and handle interactive confirmation prompts (`waiting`) [3]. |
| `manus task send <task_id> "<message>"` | Continue a multi-turn conversation with an active or waiting task [3]. |
| `manus task confirm <task_id> <event_id> [options]` | Manually confirm or reject pending actions (`--accept`, `--reject`, `--input '<json>'`) [3]. |

### Projects (`manus project`)
| Command | Description |
| :--- | :--- |
| `manus project create <name> [--instruction TEXT]` | Create a new project with shared instructions that apply automatically to tasks [4]. |
| `manus project list` | List all available projects in your account [4]. |

### Files (`manus file`)
| Command | Description |
| :--- | :--- |
| `manus file upload <path>` | Upload local files (PDFs, images, CSVs) via presigned URLs for task attachments [5]. |

### Browser & Configuration (`manus browser` / `manus config`)
| Command | Description |
| :--- | :--- |
| `manus browser list` | List online connected browser clients for `needConnectMyBrowser` waiting events [6]. |
| `manus config set <key> <value>` | Set persistent configuration values (e.g., base URL overrides) [7]. |
| `manus config list` | Display current configuration settings with automatic API key redaction [7]. |

---

## 🌐 Global Options

Every command supports the following global flags:
- `--json`: Output structured machine-readable JSON for scripting and automation pipelines.
- `--verbose` / `--debug`: Print redacted raw HTTP request and response logs for troubleshooting.
- `--base-url <url>`: Override the default API base URL (`https://api.manus.ai`).
- `--no-color`: Disable colored Rich terminal formatting.

---

## 🛠️ Testing & Development

Run the test suite using `pytest` and `respx` for HTTP mocking:
```bash
pytest
```

Run linters and format checks:
```bash
ruff check src tests
black --check src tests
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 📚 References

- [1] Manus API v2 Introduction: `https://open.manus.ai/docs/v2/introduction`
- [2] Manus Authentication Guide: `https://open.manus.ai/docs/v2/authentication.md`
- [3] Manus Task Lifecycle Guide: `https://open.manus.ai/docs/v2/task-lifecycle.md`
- [4] Manus Projects Documentation: `https://open.manus.ai/docs/v2/project.create.md`
- [5] Manus Files Documentation: `https://open.manus.ai/docs/v2/file.upload.md`
- [6] Manus Browser Integration: `https://open.manus.ai/docs/v2/browser.onlineList.md`
- [7] Manus CLI Configuration: `https://open.manus.ai/docs/v2/introduction`
