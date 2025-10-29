"""Device tracker platform for UniFi Network Pro."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import ScannerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Consider a device away if not seen for 5 minutes
AWAY_THRESHOLD = timedelta(minutes=5)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UniFi Network Pro device tracker."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    @callback
    def async_update_items() -> None:
        """Update tracked devices."""
        tracked_devices = {}
        clients = coordinator.data.get("clients", [])

        for client in clients:
            mac = client.get("mac")
            if not mac:
                continue

            if mac not in tracked_devices:
                tracked_devices[mac] = UniFiNetworkDevice(coordinator, entry, client)

        # Add new entities
        new_entities = [
            device
            for mac, device in tracked_devices.items()
            if mac not in {entity.unique_id for entity in hass.data[DOMAIN].get(f"{entry.entry_id}_trackers", [])}
        ]

        if new_entities:
            async_add_entities(new_entities)
            hass.data[DOMAIN].setdefault(f"{entry.entry_id}_trackers", []).extend(new_entities)

    # Initial setup
    hass.data[DOMAIN].setdefault(f"{entry.entry_id}_trackers", [])
    async_update_items()

    # Register update callback
    coordinator.async_add_listener(async_update_items)


class UniFiNetworkDevice(CoordinatorEntity, ScannerEntity):
    """Representation of a network device."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        client_data: dict,
    ) -> None:
        """Initialize the device."""
        super().__init__(coordinator)
        self._mac = client_data.get("mac")
        self._attr_unique_id = self._mac
        self._entry_id = entry.entry_id
        self._update_client_data(client_data)

    def _update_client_data(self, client_data: dict) -> None:
        """Update client data."""
        self._client_data = client_data
        self._hostname = client_data.get("hostname") or client_data.get("name") or "Unknown"
        self._ip = client_data.get("ip")
        self._last_seen = client_data.get("last_seen", 0)

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._hostname

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.ROUTER

    @property
    def is_connected(self) -> bool:
        """Return true if the device is connected."""
        # Update client data from coordinator
        clients = self.coordinator.data.get("clients", [])
        current_client = next(
            (client for client in clients if client.get("mac") == self._mac),
            None,
        )

        if current_client:
            self._update_client_data(current_client)
            last_seen_dt = datetime.fromtimestamp(self._last_seen, tz=dt_util.UTC)
            return dt_util.utcnow() - last_seen_dt < AWAY_THRESHOLD

        return False

    @property
    def ip_address(self) -> str | None:
        """Return the IP address."""
        return self._ip

    @property
    def mac_address(self) -> str:
        """Return the MAC address."""
        return self._mac

    @property
    def hostname(self) -> str:
        """Return the hostname."""
        return self._hostname

    @property
    def extra_state_attributes(self) -> dict:
        """Return entity specific state attributes."""
        attributes = {
            "mac": self._mac,
            "ip": self._ip,
            "hostname": self._hostname,
        }

        # Add additional attributes from client data
        if "connection" in self._client_data:
            attributes["connection_type"] = self._client_data["connection"]

        if "essid" in self._client_data:
            attributes["wifi_network"] = self._client_data["essid"]

        if "signal" in self._client_data:
            attributes["signal_strength"] = self._client_data["signal"]

        if "rx_bytes" in self._client_data:
            attributes["rx_bytes"] = self._client_data["rx_bytes"]

        if "tx_bytes" in self._client_data:
            attributes["tx_bytes"] = self._client_data["tx_bytes"]

        if "uptime" in self._client_data:
            attributes["uptime"] = self._client_data["uptime"]

        if "tx_rate" in self._client_data:
            attributes["tx_rate"] = self._client_data["tx_rate"]

        if "rx_rate" in self._client_data:
            attributes["rx_rate"] = self._client_data["rx_rate"]

        if "channel" in self._client_data:
            attributes["wifi_channel"] = self._client_data["channel"]

        if "ap_mac" in self._client_data:
            attributes["access_point"] = self._client_data["ap_mac"]

        if "is_wired" in self._client_data:
            attributes["is_wired"] = self._client_data["is_wired"]

        return attributes

    @property
    def device_info(self) -> dict:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._mac)},
            "name": self._hostname,
            "manufacturer": self._client_data.get("oui", "Unknown"),
            "model": self._client_data.get("os_name", "Network Device"),
            "via_device": (DOMAIN, self._entry_id),
        }
