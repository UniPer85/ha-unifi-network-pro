"""UniFi Network Pro integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .unifi_client import UniFiClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.DEVICE_TRACKER]
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up UniFi Network Pro from a config entry."""
    host = entry.data[CONF_HOST]
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    api_token = entry.data.get("api_token")
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, False)

    session = async_get_clientsession(hass, verify_ssl=verify_ssl)

    if api_token:
        # Using API token authentication
        _LOGGER.info("Setting up UniFi integration with API token")
        client = UniFiClient(
            host,
            session=session,
            verify_ssl=verify_ssl,
            api_token=api_token,
        )
    else:
        # Using username/password authentication
        _LOGGER.info("Setting up UniFi integration with username/password")
        # Create cookie storage path for persistent sessions
        storage_path = Path(hass.config.path(f".storage/{DOMAIN}"))
        storage_path.mkdir(parents=True, exist_ok=True)
        cookie_file = storage_path / f"{entry.entry_id}_cookies.json"

        client = UniFiClient(
            host,
            username=username,
            password=password,
            session=session,
            verify_ssl=verify_ssl,
            cookie_file=cookie_file,
        )

    try:
        _LOGGER.info("Connecting to UniFi controller at %s", host)
        await client.login()

        # Check available sites and log them for debugging
        sites = await client.get_sites()
        if sites:
            _LOGGER.info("Found %d site(s) on controller", len(sites))
            for site in sites:
                _LOGGER.info("  - Site: %s (ID: %s)", site.get("desc", "Unknown"), site.get("name", "unknown"))
        else:
            _LOGGER.warning("No sites found - this might cause issues with device discovery")

    except Exception as err:
        _LOGGER.error("Error connecting to UniFi controller: %s", err)
        _LOGGER.error("If you have 2FA enabled, ensure you approved the login request")
        raise ConfigEntryNotReady from err

    async def async_update_data():
        """Fetch data from UniFi controller."""
        try:
            devices = await client.get_clients()
            stats = await client.get_system_stats()
            return {
                "clients": devices,
                "stats": stats,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with UniFi: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        client = hass.data[DOMAIN][entry.entry_id]["client"]
        await client.logout()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
