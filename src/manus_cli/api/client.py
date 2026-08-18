"""API client for the Manus platform using httpx."""

import time
from typing import Any

import httpx

from manus_cli.errors import APIError, AuthError, RateLimitError
from manus_cli.output import err_console


class APIClient:
    """Client for the Manus REST API v2."""

    def __init__(self, base_url: str, api_key: str | None = None, debug: bool = False):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.debug = debug
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=60.0,
            follow_redirects=False,
        )

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["x-manus-api-key"] = self.api_key
        return headers

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make an HTTP request with safe debug logging and retry logic."""
        req_headers = self._get_headers()
        if headers:
            req_headers.update(headers)

        if self.debug:
            err_console.print(
                f"[debug] {method} {self.base_url}{path} " f"params={params!r} payload=[omitted]"
            )

        max_retries = 3
        backoff_factor = 1.0

        for attempt in range(max_retries + 1):
            try:
                response = self.client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json_data,
                    headers=req_headers,
                )

                if self.debug:
                    err_console.print(
                        f"[debug] Response status={response.status_code} "
                        f"content_length={response.headers.get('content-length', 'unknown')}"
                    )

                try:
                    data = response.json()
                except ValueError:
                    if response.status_code >= 400:
                        raise APIError(
                            message=f"HTTP {response.status_code}: response body omitted",
                            status_code=response.status_code,
                        )
                    data = {"ok": True, "result": response.text}

                if isinstance(data, dict) and "ok" in data and not data["ok"]:
                    err_info = data.get("error", {})
                    err_code = err_info.get("code", "unknown")
                    err_msg = err_info.get("message", "Unknown API error")
                    req_id = data.get("request_id")

                    if err_code == "rate_limited" or response.status_code == 429:
                        retry_after_header = response.headers.get("Retry-After")
                        retry_after = (
                            int(retry_after_header)
                            if retry_after_header and retry_after_header.isdigit()
                            else int(backoff_factor)
                        )
                        if attempt < max_retries:
                            time.sleep(retry_after)
                            backoff_factor *= 2
                            continue
                        raise RateLimitError(
                            message=err_msg, request_id=req_id, retry_after=retry_after
                        )

                    if err_code in (
                        "permission_denied",
                        "unauthorized",
                    ) or response.status_code in (
                        401,
                        403,
                    ):
                        raise AuthError(f"Authentication/Permission error: {err_msg}")

                    raise APIError(
                        message=err_msg,
                        code=err_code,
                        status_code=response.status_code,
                        request_id=req_id,
                    )

                if response.status_code >= 400:
                    raise APIError(
                        message=f"HTTP {response.status_code}: response body omitted",
                        status_code=response.status_code,
                    )

                return data

            except httpx.TransportError as exc:
                if attempt < max_retries:
                    time.sleep(backoff_factor)
                    backoff_factor *= 2
                    continue
                raise APIError(f"Network transport error: {exc}") from exc

        raise APIError("Max retries exceeded for rate limits.")

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, json_data: dict[str, Any] | None = None) -> Any:
        return self.request("POST", path, json_data=json_data)

    def put(self, path: str, json_data: dict[str, Any] | None = None) -> Any:
        return self.request("PUT", path, json_data=json_data)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)
