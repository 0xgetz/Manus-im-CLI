"""Custom exceptions for the Manus CLI."""


class ManusError(Exception):
    """Base exception for Manus CLI."""

    exit_code = 1


class ConfigError(ManusError):
    """Configuration related errors."""

    exit_code = 2


class AuthError(ManusError):
    """Authentication or authorization errors (exit code 3)."""

    exit_code = 3


class APIError(ManusError):
    """API error response from Manus platform."""

    def __init__(
        self,
        message: str,
        code: str = "unknown",
        status_code: int = 400,
        request_id: str | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.request_id = request_id

        if code in ("permission_denied", "unauthorized"):
            self.exit_code = 3
        elif code == "rate_limited":
            self.exit_code = 4
        elif code in ("invalid_argument", "not_found"):
            self.exit_code = 2
        else:
            self.exit_code = 1


class RateLimitError(APIError):
    """Rate limit exceeded error (exit code 4)."""

    def __init__(self, message: str, request_id: str | None = None, retry_after: int | None = None):
        super().__init__(message, code="rate_limited", status_code=429, request_id=request_id)
        self.retry_after = retry_after
        self.exit_code = 4
