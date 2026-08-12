"""Configuration management for Manus CLI."""

import os
import pathlib
from typing import Any

import tomli_w
import tomllib

CONFIG_DIR = pathlib.Path.home() / ".config" / "manus"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_BASE_URL = "https://api.manus.ai"


def ensure_config_dir() -> None:
    """Ensure config directory exists with secure permissions (0700)."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        os.chmod(CONFIG_DIR, 0o700)


def load_config() -> dict[str, Any]:
    """Load configuration from ~/.config/manus/config.toml."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to ~/.config/manus/config.toml with secure permissions (0600)."""
    ensure_config_dir()
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(config, f)
    os.chmod(CONFIG_FILE, 0o600)


def get_api_key(cli_override: str | None = None) -> str | None:
    """Get API key from CLI override, env var MANUS_API_KEY, or config file."""
    if cli_override:
        return cli_override
    env_key = os.environ.get("MANUS_API_KEY")
    if env_key:
        return env_key
    config = load_config()
    return config.get("api_key")


def get_base_url(cli_override: str | None = None) -> str:
    """Get base URL from CLI override, env var MANUS_BASE_URL, config file, or default."""
    if cli_override:
        return cli_override
    env_url = os.environ.get("MANUS_BASE_URL")
    if env_url:
        return env_url
    config = load_config()
    return config.get("base_url", DEFAULT_BASE_URL)


def set_config_value(key: str, value: Any) -> None:
    """Set a configuration value."""
    config = load_config()
    config[key] = value
    save_config(config)


def get_config_value(key: str) -> Any:
    """Get a configuration value."""
    config = load_config()
    return config.get(key)
