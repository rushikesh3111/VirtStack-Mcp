"""
virtstack_client.py — Safe, read-only HTTP client for VirtStack.

- Auto-logs in using VIRTSTACK_USERNAME + VIRTSTACK_PASSWORD from .env
- Manages the Bearer token in memory (never on disk)
- Exposes ONLY a .get() method — raises ReadOnlyViolationError for all other methods
- Auto-retries login once if a 401 is received (handles token expiry)
"""

import logging
from typing import Any, Optional

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("virtstack_mcp.client")


class Settings(BaseSettings):
    """Configuration loaded from .env file."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    virtstack_api_url: str = "http://localhost:8000"
    virtstack_username: str = "admin"
    virtstack_password: str = "password"


class ReadOnlyViolationError(Exception):
    """Raised when someone tries to make a non-GET request through this client."""
    pass


class VirtStackClient:
    """
    Async HTTP client that enforces read-only access to the VirtStack API.

    Usage:
        client = VirtStackClient()
        await client.login()
        data = await client.get("/api/v1/hosts")
    """

    def __init__(self):
        self._settings = Settings()
        self._token: Optional[str] = None
        self._http = httpx.AsyncClient(
            base_url=self._settings.virtstack_api_url,
            timeout=30.0,
            verify=False,  # VirtStack uses self-signed TLS certificates
        )

    # ── Authentication ────────────────────────────────────────────────────────

    async def login(self) -> None:
        """Login with username/password and store the token in memory."""
        logger.info("Logging in to VirtStack at %s", self._settings.virtstack_api_url)
        payload = {
            "username": self._settings.virtstack_username,
            "password": self._settings.virtstack_password,
        }
        try:
            response = await self._http.post("/api/v1/auth/login", json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ConnectionError(
                f"VirtStack login failed (HTTP {exc.response.status_code}): "
                f"{exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise ConnectionError(
                f"VirtStack is unreachable at {self._settings.virtstack_api_url}: {exc}"
            ) from exc

        data = response.json()
        self._token = data.get("access_token")
        if not self._token:
            raise ConnectionError(
                f"Login response did not contain access_token. Got: {data}"
            )
        logger.info("Login successful for user: %s", data.get("username", "unknown"))

    async def ensure_logged_in(self) -> None:
        """Login if we don't yet have a token."""
        if not self._token:
            await self.login()

    # ── Read-Only GET ─────────────────────────────────────────────────────────

    async def get(self, path: str, params: Optional[dict] = None) -> Any:
        """
        Send a GET request to VirtStack. Auto-logs in on first call.
        Retries login once on 401 (token expired).

        Args:
            path: API path, e.g. "/api/v1/hosts"
            params: Optional query parameters, e.g. {"limit": 50}

        Returns:
            Parsed JSON response (dict or list).

        Raises:
            ReadOnlyViolationError: If this method is misused (internal guard).
            httpx.HTTPStatusError: On non-2xx responses.
            ConnectionError: If VirtStack is unreachable.
        """
        await self.ensure_logged_in()
        return await self._get_with_retry(path, params)

    async def _get_with_retry(self, path: str, params: Optional[dict]) -> Any:
        """Internal: GET with one auto-retry on 401 (re-login)."""
        response = await self._http.get(
            path,
            params=params,
            headers={"Authorization": f"Bearer {self._token}"},
        )
        if response.status_code == 401:
            logger.warning("Token expired, re-logging in...")
            await self.login()
            response = await self._http.get(
                path,
                params=params,
                headers={"Authorization": f"Bearer {self._token}"},
            )
        response.raise_for_status()
        # Handle plain-text responses (e.g. VM XML)
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    # ── Safety Guards (Write-Block) ───────────────────────────────────────────

    async def post(self, *args, **kwargs):
        raise ReadOnlyViolationError(
            "POST requests are blocked. This MCP server is strictly read-only."
        )

    async def put(self, *args, **kwargs):
        raise ReadOnlyViolationError(
            "PUT requests are blocked. This MCP server is strictly read-only."
        )

    async def patch(self, *args, **kwargs):
        raise ReadOnlyViolationError(
            "PATCH requests are blocked. This MCP server is strictly read-only."
        )

    async def delete(self, *args, **kwargs):
        raise ReadOnlyViolationError(
            "DELETE requests are blocked. This MCP server is strictly read-only."
        )

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    async def __aenter__(self):
        await self.ensure_logged_in()
        return self

    async def __aexit__(self, *args):
        await self.close()


# ── Module-level singleton (shared by all tool modules) ───────────────────────
client = VirtStackClient()
