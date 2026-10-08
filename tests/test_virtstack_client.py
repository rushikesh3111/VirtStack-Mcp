"""
tests/test_virtstack_client.py — Tests for VirtStack read-only client.

Tests:
  1. write methods (post/put/patch/delete) raise ReadOnlyViolationError
  2. get() calls the correct URL
  3. auto-retry on 401
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import AsyncMock, MagicMock, patch
from virtstack_client import VirtStackClient, ReadOnlyViolationError


# ── Write-Block Tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_post_raises_readonly():
    """POST must always raise ReadOnlyViolationError."""
    c = VirtStackClient()
    with pytest.raises(ReadOnlyViolationError):
        await c.post("/api/v1/vms", json={})


@pytest.mark.asyncio
async def test_put_raises_readonly():
    """PUT must always raise ReadOnlyViolationError."""
    c = VirtStackClient()
    with pytest.raises(ReadOnlyViolationError):
        await c.put("/api/v1/vms/123", json={})


@pytest.mark.asyncio
async def test_patch_raises_readonly():
    """PATCH must always raise ReadOnlyViolationError."""
    c = VirtStackClient()
    with pytest.raises(ReadOnlyViolationError):
        await c.patch("/api/v1/vms/123", json={})


@pytest.mark.asyncio
async def test_delete_raises_readonly():
    """DELETE must always raise ReadOnlyViolationError."""
    c = VirtStackClient()
    with pytest.raises(ReadOnlyViolationError):
        await c.delete("/api/v1/vms/123")


# ── Login Test ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_stores_token():
    """Login should parse access_token from response and store it."""
    c = VirtStackClient()
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "access_token": "test_token_abc",
        "username": "admin",
    }
    c._http.post = AsyncMock(return_value=mock_response)

    await c.login()
    assert c._token == "test_token_abc"


# ── GET Test ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_sends_bearer_token():
    """GET should include the Bearer token in the Authorization header."""
    c = VirtStackClient()
    c._token = "my_test_token"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/json"}
    mock_response.json.return_value = [{"id": "host-1", "name": "node-01"}]
    mock_response.raise_for_status = MagicMock()
    c._http.get = AsyncMock(return_value=mock_response)

    result = await c.get("/api/v1/hosts")
    assert result == [{"id": "host-1", "name": "node-01"}]

    # Check Authorization header was passed
    call_kwargs = c._http.get.call_args[1]
    assert "Authorization" in call_kwargs.get("headers", {})
    assert call_kwargs["headers"]["Authorization"] == "Bearer my_test_token"


@pytest.mark.asyncio
async def test_get_retries_on_401():
    """GET should re-login and retry when it receives a 401."""
    c = VirtStackClient()
    c._token = "expired_token"

    # First call returns 401, second returns 200
    expired_response = MagicMock()
    expired_response.status_code = 401
    expired_response.raise_for_status = MagicMock()

    ok_response = MagicMock()
    ok_response.status_code = 200
    ok_response.headers = {"content-type": "application/json"}
    ok_response.json.return_value = {"status": "ok"}
    ok_response.raise_for_status = MagicMock()

    c._http.get = AsyncMock(side_effect=[expired_response, ok_response])
    c.login = AsyncMock()

    result = await c._get_with_retry("/api/v1/health", None)
    assert result == {"status": "ok"}
    c.login.assert_called_once()
