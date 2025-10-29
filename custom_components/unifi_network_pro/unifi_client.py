"""UniFi API client for UDM Pro Max."""
from __future__ import annotations

import logging
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


class UniFiClient:
    """UniFi API client."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
        verify_ssl: bool = False,
    ) -> None:
        """Initialize the UniFi client."""
        self.host = host.rstrip("/")
        self.username = username
        self.password = password
        self.session = session
        self.verify_ssl = verify_ssl
        self.site_id = DEFAULT_SITE_ID
        self._headers = {
            "Content-Type": "application/json",
        }

    async def login(self) -> bool:
        """Log in to the UniFi controller."""
        url = f"{self.host}{API_LOGIN}"
        data = {
            "username": self.username,
            "password": self.password,
            "remember": True,
        }

        try:
            async with self.session.post(
                url, json=data, headers=self._headers, ssl=self.verify_ssl
            ) as response:
                if response.status == 200:
                    _LOGGER.info("Successfully logged in to UniFi controller")
                    return True
                else:
                    error_text = await response.text()
                    _LOGGER.error(
                        "Failed to login: status=%s, response=%s",
                        response.status,
                        error_text,
                    )
                    return False
        except Exception as err:
            _LOGGER.error("Login error: %s", err)
            raise

    async def logout(self) -> None:
        """Log out from the UniFi controller."""
        url = f"{self.host}{API_LOGOUT}"
        try:
            async with self.session.post(
                url, headers=self._headers, ssl=self.verify_ssl
            ) as response:
                if response.status == 200:
                    _LOGGER.info("Successfully logged out from UniFi controller")
        except Exception as err:
            _LOGGER.error("Logout error: %s", err)

    async def _make_request(self, endpoint: str) -> dict[str, Any]:
        """Make an API request."""
        url = f"{self.host}{endpoint.format(site=self.site_id)}"

        try:
            async with self.session.get(
                url, headers=self._headers, ssl=self.verify_ssl, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                elif response.status == 401:
                    _LOGGER.warning("Session expired, attempting to re-login")
                    await self.login()
                    # Retry the request
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
