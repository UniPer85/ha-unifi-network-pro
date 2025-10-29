"""Sensor platform for UniFi Network Pro."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfDataRate,
    UnitOfInformation,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class UniFiSensorEntityDescription(SensorEntityDescription):
    """Describes UniFi sensor entity."""

    value_fn: Callable[[dict], any] = None


SENSOR_DESCRIPTIONS: tuple[UniFiSensorEntityDescription, ...] = (
    UniFiSensorEntityDescription(
        key="connected_clients",
        name="Connected Clients",
        icon="mdi:devices",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("stats", {}).get("connected_clients", 0),
    ),
    UniFiSensorEntityDescription(
        key="cpu_usage",
        name="CPU Usage",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cpu-64-bit",
        value_fn=lambda data: round(data.get("stats", {}).get("cpu_usage", 0), 1),
    ),
    UniFiSensorEntityDescription(
        key="memory_usage",
        name="Memory Usage",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:memory",
        value_fn=lambda data: round(data.get("stats", {}).get("memory_usage", 0), 1),
    ),
    UniFiSensorEntityDescription(
        key="uptime",
        name="Uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
        value_fn=lambda data: data.get("stats", {}).get("uptime", 0),
    ),
    UniFiSensorEntityDescription(
        key="wan_ip",
        name="WAN IP Address",
        icon="mdi:ip-network",
        value_fn=lambda data: data.get("stats", {}).get("wan_ip", "Unknown"),
    ),
    UniFiSensorEntityDescription(
        key="wan_rx_bytes",
        name="WAN Download Total",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:download-network",
        value_fn=lambda data: data.get("stats", {}).get("wan_rx_bytes", 0),
    ),
    UniFiSensorEntityDescription(
        key="wan_tx_bytes",
        name="WAN Upload Total",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:upload-network",
        value_fn=lambda data: data.get("stats", {}).get("wan_tx_bytes", 0),
    ),
    UniFiSensorEntityDescription(
        key="lan_rx_bytes",
        name="LAN Download Total",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:download-network-outline",
        value_fn=lambda data: data.get("stats", {}).get("lan_rx_bytes", 0),
    ),
    UniFiSensorEntityDescription(
        key="lan_tx_bytes",
        name="LAN Upload Total",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:upload-network-outline",
        value_fn=lambda data: data.get("stats", {}).get("lan_tx_bytes", 0),
    ),
    UniFiSensorEntityDescription(
        key="wan_download_mbps",
        name="WAN Download Speed",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: round(data.get("stats", {}).get("wan_download_mbps", 0), 2),
    ),
    UniFiSensorEntityDescription(
        key="wan_upload_mbps",
        name="WAN Upload Speed",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda data: round(data.get("stats", {}).get("wan_upload_mbps", 0), 2),
    ),
    UniFiSensorEntityDescription(
        key="wan_latency",
        name="WAN Latency",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer-outline",
        value_fn=lambda data: data.get("stats", {}).get("wan_latency", 0),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UniFi Network Pro sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        UniFiNetworkProSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class UniFiNetworkProSensor(CoordinatorEntity, SensorEntity):
    """Representation of a UniFi Network Pro sensor."""

    entity_description: UniFiSensorEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        description: UniFiSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "UniFi Network",
            "manufacturer": "Ubiquiti",
            "model": "UDM Pro Max",
            "sw_version": "UniFi OS",
        }

    @property
    def native_value(self) -> any:
        """Return the state of the sensor."""
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
