"""UniFi API client for UDM Pro Max."""
from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import aiohttp

from .const import (
    API_CLIENTS,
    API_DEVICES,
    API_HEALTH,
    API_LOGIN,
    API_LOGOUT,
    API_SYSTEM_INFO,
    DEFAULT_SITE_ID,
)

_LOGGER = logging.getLogger(__name__)

# Extended timeout for 2FA authentication (60 seconds)
LOGIN_TIMEOUT = 60


class UniFiClient:
    """UniFi API client with persistent session support."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
        verify_ssl: bool = False,
        cookie_file: Path | None = None,
    ) -> None:
        """Initialize the UniFi client.

        Args:
            host: UniFi controller host URL
            username: Username for authentication
            password: Password for authentication
            session: aiohttp ClientSession
            verify_ssl: Whether to verify SSL certificates
            cookie_file: Optional path to store session cookies for persistence
        """
        self.host = host.rstrip("/")
        self.username = username
        self.password = password
        self.session = session
        self.verify_ssl = verify_ssl
        self.site_id = DEFAULT_SITE_ID
        self.cookie_file = cookie_file
        self._headers = {
            "Content-Type": "application/json",
        }
        self._authenticated = False

        # Load saved cookies if available
        if self.cookie_file and self.cookie_file.exists():
            asyncio.create_task(self._load_cookies())

    async def _load_cookies(self) -> None:
        """Load saved cookies from file."""
        try:
            if self.cookie_file and self.cookie_file.exists():
                with open(self.cookie_file, "r") as f:
                    cookies_data = json.load(f)
                    for cookie in cookies_data:
                        self.session.cookie_jar.update_cookies({cookie["key"]: cookie["value"]})
                _LOGGER.debug("Loaded %d cookies from storage", len(cookies_data))
        except Exception as err:
            _LOGGER.warning("Failed to load cookies: %s", err)

    async def _save_cookies(self) -> None:
        """Save current cookies to file."""
        try:
            if self.cookie_file:
                cookies_data = []
                for cookie in self.session.cookie_jar:
                    cookies_data.append({
                        "key": cookie.key,
                        "value": cookie.value,
                    })

                # Ensure parent directory exists
                self.cookie_file.parent.mkdir(parents=True, exist_ok=True)

                with open(self.cookie_file, "w") as f:
                    json.dump(cookies_data, f)
                _LOGGER.debug("Saved %d cookies to storage", len(cookies_data))
        except Exception as err:
            _LOGGER.warning("Failed to save cookies: %s", err)

    async def login(self, timeout: int = LOGIN_TIMEOUT, retry_for_2fa: bool = True) -> bool:
        """Log in to the UniFi controller.

        Args:
            timeout: Timeout in seconds (default 60s to allow for 2FA)
            retry_for_2fa: If True, will poll for successful auth when 2FA is pending

        Returns:
            True if login successful, False otherwise
        """
        # Check if we already have valid cookies
        if self._authenticated:
            _LOGGER.debug("Already authenticated, skipping login")
            return True

        url = f"{self.host}{API_LOGIN}"
        data = {
            "username": self.username,
            "password": self.password,
            "remember": True,
        }

        start_time = asyncio.get_event_loop().time()
        attempt = 0
        last_error = None

        _LOGGER.info("Attempting login to UniFi controller (will retry for %ds if 2FA required)", timeout)
        _LOGGER.info("If you have 2FA enabled, please approve the login on your Unifi Verify app now")

        while (asyncio.get_event_loop().time() - start_time) < timeout:
            attempt += 1
            try:
                async with self.session.post(
                    url,
                    json=data,
                    headers=self._headers,
                    ssl=self.verify_ssl,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        _LOGGER.info("Successfully logged in to UniFi controller (attempt %d)", attempt)
                        self._authenticated = True
                        # Save cookies for future sessions
                        await self._save_cookies()
                        return True
                    else:
                        response_data = await response.text()

                        # Check if error indicates 2FA is pending
                        if response.status == 401 and retry_for_2fa:
                            if attempt == 1:
                                _LOGGER.warning(
                                    "Login pending 2FA approval - waiting for you to approve on Unifi Verify app..."
                                )
                            last_error = f"2FA approval pending (attempt {attempt})"
                            # Wait 2 seconds before retrying
                            await asyncio.sleep(2)
                            continue
                        else:
                            _LOGGER.error(
                                "Failed to login: status=%s, response=%s",
                                response.status,
                                response_data,
                            )
                            self._authenticated = False
                            return False

            except asyncio.TimeoutError:
                _LOGGER.debug("Login attempt %d timed out, retrying...", attempt)
                last_error = "Connection timeout"
                await asyncio.sleep(2)
                continue
            except Exception as err:
                if retry_for_2fa and (asyncio.get_event_loop().time() - start_time) < timeout:
                    _LOGGER.debug("Login attempt %d failed: %s, retrying...", attempt, err)
                    last_error = str(err)
                    await asyncio.sleep(2)
                    continue
                else:
                    _LOGGER.error("Login error: %s", err)
                    self._authenticated = False
                    raise

        # Timeout reached
        _LOGGER.error(
            "Login timeout after %ds - 2FA approval was not completed in time. Last error: %s",
            timeout,
            last_error
        )
        self._authenticated = False
        return False

    async def logout(self) -> None:
        """Log out from the UniFi controller and clear saved cookies."""
        url = f"{self.host}{API_LOGOUT}"
        try:
            async with self.session.post(
                url, headers=self._headers, ssl=self.verify_ssl
            ) as response:
                if response.status == 200:
                    _LOGGER.info("Successfully logged out from UniFi controller")

            # Clear authentication state and saved cookies
            self._authenticated = False
            self.session.cookie_jar.clear()

            # Remove cookie file
            if self.cookie_file and self.cookie_file.exists():
                self.cookie_file.unlink()
                _LOGGER.debug("Removed saved cookies")

        except Exception as err:
            _LOGGER.error("Logout error: %s", err)

    async def _make_request(self, endpoint: str, retry_on_401: bool = True) -> dict[str, Any]:
        """Make an API request.

        Args:
            endpoint: API endpoint to call
            retry_on_401: Whether to retry after re-authentication on 401 errors

        Returns:
            API response data
        """
        url = f"{self.host}{endpoint.format(site=self.site_id)}"

        try:
            async with self.session.get(
                url, headers=self._headers, ssl=self.verify_ssl, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Mark as authenticated if request succeeds
                    self._authenticated = True
                    return data.get("data", [])
                elif response.status == 401:
                    _LOGGER.warning("Session expired (401), attempting to re-login")
                    self._authenticated = False

                    if not retry_on_401:
                        _LOGGER.error("Re-authentication failed")
                        return []

                    # Re-authenticate
                    await self.login()

                    # Retry the request once
                    async with self.session.get(
                        url, headers=self._headers, ssl=self.verify_ssl, timeout=aiohttp.ClientTimeout(total=10)
                    ) as retry_response:
                        if retry_response.status == 200:
                            data = await retry_response.json()
                            return data.get("data", [])
                        else:
                            _LOGGER.error("Retry failed with status: %s", retry_response.status)
                            return []
                else:
                    error_text = await response.text()
                    _LOGGER.error(
                        "API request failed: status=%s, response=%s",
                        response.status,
                        error_text,
                    )
                    return []
        except aiohttp.ClientError as err:
            _LOGGER.error("Client error during API request: %s", err)
            return []
        except Exception as err:
            _LOGGER.error("Unexpected error during API request: %s", err)
            return []

    async def get_clients(self) -> list[dict[str, Any]]:
        """Get all connected clients."""
        return await self._make_request(API_CLIENTS)

    async def get_devices(self) -> list[dict[str, Any]]:
        """Get all UniFi devices."""
        return await self._make_request(API_DEVICES)

    async def get_health(self) -> list[dict[str, Any]]:
        """Get system health information."""
        return await self._make_request(API_HEALTH)

    async def get_system_stats(self) -> dict[str, Any]:
        """Get system statistics."""
        devices = await self.get_devices()
        health = await self.get_health()
        clients = await self.get_clients()

        stats = {
            "connected_clients": len(clients),
            "total_devices": len(devices),
        }

        # Parse UDM Pro Max specific stats
        for device in devices:
            if device.get("type") == "udm" or device.get("model", "").startswith("UDM"):
                stats["cpu_usage"] = device.get("system-stats", {}).get("cpu", 0)
                stats["memory_usage"] = device.get("system-stats", {}).get("mem", 0)
                stats["uptime"] = device.get("uptime", 0)

                # Get network stats
                if "stat" in device:
                    device_stat = device["stat"]
                    stats["wan_rx_bytes"] = device_stat.get("wan-rx_bytes", 0)
                    stats["wan_tx_bytes"] = device_stat.get("wan-tx_bytes", 0)
                    stats["lan_rx_bytes"] = device_stat.get("rx_bytes", 0)
                    stats["lan_tx_bytes"] = device_stat.get("tx_bytes", 0)

                # Get WAN IP
                if "wan1" in device:
                    stats["wan_ip"] = device["wan1"].get("ip", "Unknown")

        # Parse health data
        for subsystem in health:
            subsystem_name = subsystem.get("subsystem", "")
            if subsystem_name == "wan":
                stats["wan_status"] = subsystem.get("status", "unknown")
                stats["wan_latency"] = subsystem.get("latency", 0)
                # Speed tests might be in speedtest_status
                if "speedtest_status" in subsystem:
                    speedtest = subsystem["speedtest_status"]
                    stats["wan_download_mbps"] = speedtest.get("xput_download", 0)
                    stats["wan_upload_mbps"] = speedtest.get("xput_upload", 0)

        return stats
