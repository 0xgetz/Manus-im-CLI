"""Configuration management for Manus CLI."""

import os
import pathlib
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import tomli_w

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

CONFIG_DIR = pathlib.Path.home() / ".config" / "manus"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_BASE_URL = "https://api.manus.ai"
TRUSTED_API_HOSTS = frozenset({"api.manus.ai"})
SENSITIVE_CONFIG_KEYS = frozenset({"api_key"})


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
    except (OSError, tomllib.TOMLDecodeError):
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


def validate_base_url(base_url: str, allow_custom: bool = False) -> str:
    """Validate and normalize an API URL before it can receive API credentials.

    The official API host is the only allowed target by default. A user must opt in
    explicitly with ``--allow-custom-base-url`` before credentials can be sent to
    another HTTPS endpoint.
    """
    parsed = urlsplit(base_url)
    hostname = parsed.hostname.lower() if parsed.hostname else None

    if parsed.scheme.lower() != "https":
        raise ValueError("API base URL must use HTTPS.")
    if not hostname:
        raise ValueError("API base URL must include a hostname.")
    if parsed.username or parsed.password:
        raise ValueError("API base URL must not contain embedded credentials.")
    if parsed.query or parsed.fragment:
        raise ValueError("API base URL must not contain a query string or fragment.")
    if hostname not in TRUSTED_API_HOSTS and not allow_custom:
        allowed = ", ".join(sorted(TRUSTED_API_HOSTS))
        raise ValueError(
            f"Refusing to send credentials to untrusted host '{hostname}'. "
            f"Use --allow-custom-base-url only when you trust the endpoint. "
            f"Trusted host: {allowed}."
        )

    netloc = hostname
    if parsed.port and parsed.port != 443:
        netloc = f"{hostname}:{parsed.port}"
    return urlunsplit(("https", netloc, parsed.path.rstrip("/"), "", "")) or "https://" + netloc


def get_base_url(cli_override: str | None = None, allow_custom: bool = False) -> str:
    """Get and validate API base URL from CLI, environment, config, or default."""
    base_url = cli_override or os.environ.get("MANUS_BASE_URL")
    if not base_url:
        base_url = load_config().get("base_url", DEFAULT_BASE_URL)
    return validate_base_url(str(base_url), allow_custom=allow_custom)


def set_config_value(key: str, value: Any) -> None:
    """Set a configuration value."""
    config = load_config()
    config[key] = value
    save_config(config)


def get_config_value(key: str) -> Any:
    """Get a configuration value."""
    config = load_config()
    return config.get(key)


def is_sensitive_config_key(key: str) -> bool:
    """Return whether a configuration key must be redacted by default."""
    return key.lower() in SENSITIVE_CONFIG_KEYS
