# Contributing to Manus-im-CLI

First off, thank you for taking the time to contribute to **Manus-im-CLI**! [1] We appreciate community involvement in building a robust, developer-friendly command-line interface for the Manus AI agent platform [2].

Please review this guide to understand our development workflow, coding standards, testing requirements, and pull request process.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started (Development Setup)](#getting-started-development-setup)
3. [Repository Architecture](#repository-architecture)
4. [Coding Standards & Guidelines](#coding-standards--guidelines)
5. [Testing & Quality Assurance](#testing--quality-assurance)
6. [Submitting Contributions (Pull Requests)](#submitting-contributions-pull-requests)
7. [Reporting Issues](#reporting-issues)

---

## 🤝 Code of Conduct

By participating in this project, you agree to maintain a respectful, welcoming, and professional environment for all contributors and maintainers.

---

## 💻 Getting Started (Development Setup)

To set up your local development environment for contributing to `Manus-im-CLI`, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/0xgetz/Manus-im-CLI.git
   cd Manus-im-CLI
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Package with Development Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -e .[dev]
   ```

4. **Verify Installation and Test Suite**:
   ```bash
   pytest
   ```

---

## 🏗️ Repository Architecture

The codebase adheres to a clean, modular architecture separating network clients, CLI command definitions, and formatting utilities [3]:

```
Manus-im-CLI/
├── src/
│   └── manus_cli/
│       ├── __init__.py
│       ├── __main__.py
│       ├── api/               # REST API v2 client layer
│       │   ├── client.py      # HTTPX client with rate-limit retries & auth
│       │   ├── files.py       # File upload & browser API helpers
│       │   ├── models.py      # Pydantic data schemas
│       │   ├── projects.py    # Project management APIs
│       │   └── tasks.py       # Task lifecycle APIs
│       ├── commands/          # Typer CLI command tree
│       │   ├── auth.py        # Authentication & whoami
│       │   ├── browser.py     # Browser listing
│       │   ├── config.py      # Configuration management
│       │   ├── file.py        # File uploads
│       │   ├── project.py     # Project creation & listing
│       │   └── task.py        # Task creation, list, watch, send, confirm
│       ├── config.py          # TOML configuration handler (~/.config/manus)
│       ├── errors.py          # Custom exceptions & exit codes
│       └── output.py          # Rich terminal formatting & key redaction
├── tests/
│   └── test_api.py            # Pytest suite with Respx HTTP mocks
└── pyproject.toml             # Project metadata, dependencies, and linter rules
```

---

## 📐 Coding Standards & Guidelines

We maintain strict code quality standards to ensure reliability and maintainability across all supported Python versions (`3.10`, `3.11`, `3.12`) [4]:

1. **Type Hints**: All functions, methods, and classes must include full type annotations.
2. **Formatting**: Code formatting is managed automatically by `black` (line length: `100`) [5].
3. **Linting**: We use `ruff` for fast and rigorous static analysis [5].
4. **Security**: Never hardcode API keys or credentials. Ensure API keys are automatically redacted in debug/verbose logs via `output.py`.

Before submitting code, run the local linters and formatters:
```bash
ruff check src tests
black --check src tests
```

---

## 🧪 Testing & Quality Assurance

All new features, bug fixes, or API client updates **must** include corresponding unit tests:
- HTTP requests must be mocked using `respx` to avoid making live network calls during tests [6].
- Test coverage should target the core API client layer (`api/`) and command error handling.

Run tests locally:
```bash
pytest
```

---

## 🚀 Submitting Contributions (Pull Requests)

1. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Commit Changes**:
   Write clear, concise commit messages following conventional commit guidelines (e.g., `feat(task): add support for custom polling intervals`).

3. **Run CI Checks Locally**:
   Ensure `pytest`, `ruff`, and `black` pass successfully without errors.

4. **Push and Open a Pull Request**:
   Push your branch to GitHub and open a pull request against the `master` branch. Provide a detailed description of your changes and reference any related issues [7].

---

## 🐞 Reporting Issues

If you encounter bugs, rate-limiting issues, or have feature requests, please open an issue on the [GitHub Issues page](https://github.com/0xgetz/Manus-im-CLI/issues) with:
- A clear, descriptive title.
- Steps to reproduce the unexpected behavior.
- Expected vs. actual behavior.
- Environment details (OS, Python version, CLI version).

---

## 📚 References

- [1] Manus API v2 Introduction: `https://open.manus.ai/docs/v2/introduction`
- [2] Manus Authentication Guide: `https://open.manus.ai/docs/v2/authentication.md`
- [3] Manus Task Lifecycle Guide: `https://open.manus.ai/docs/v2/task-lifecycle.md`
- [4] Python Packaging PEP 621: `https://peps.python.org/pep-0621/`
- [5] Ruff Linter Documentation: `https://beta.ruff.rs/docs/`
- [6] Respx HTTP Mocker: `https://github.com/lundberg/respx`
- [7] GitHub Pull Request Documentation: `https://docs.github.com/en/pull-requests`
