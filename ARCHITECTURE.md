# Architecture Documentation - UniFi Network Pro

This document provides technical details about the UniFi Network Pro integration architecture.

## Overview

The integration follows Home Assistant's standard integration pattern with a coordinator-based architecture for efficient data management and updates.

## Component Structure

```
custom_components/unifi_network_pro/
├── __init__.py              # Integration setup and coordinator
├── config_flow.py           # UI-based configuration flow
├── const.py                 # Constants and configuration
├── device_tracker.py        # Device tracker platform
├── manifest.json            # Integration metadata
├── sensor.py                # Sensor platform
├── strings.json             # UI strings
├── unifi_client.py          # UniFi API client
└── translations/
    └── en.json              # English translations
```

## Component Responsibilities

### `__init__.py` - Integration Core

**Purpose**: Main integration setup and coordination

**Key Functions**:
- `async_setup_entry()`: Initialize integration from config entry
- `async_unload_entry()`: Clean up when integration is removed
- Creates and manages DataUpdateCoordinator

**Data Flow**:
```python
Config Entry → Client Setup → Coordinator Creation → Platform Setup
```

**Coordinator Configuration**:
- Update interval: 30 seconds
- Handles authentication refresh
- Manages data updates for all platforms
- Provides data to all entities

### `config_flow.py` - Configuration

**Purpose**: User-friendly configuration through Home Assistant UI

**Features**:
- Input validation
- Connection testing
- Credential verification
- Error handling with user-friendly messages

**Flow Diagram**:
```
User Input → Validation → API Test → Create Entry
     ↓
  Errors → Display → Retry
```

### `const.py` - Constants

**Purpose**: Centralized configuration and constants

**Contains**:
- Domain identifier
- API endpoint paths
- Sensor types and keys
- Attribute names
- Default values

### `unifi_client.py` - API Client

**Purpose**: Communication with UniFi Controller API

**Key Methods**:

| Method | Purpose | Returns |
|--------|---------|---------|
| `login()` | Authenticate with controller | bool |
| `logout()` | End session | None |
| `get_clients()` | Fetch connected devices | list[dict] |
| `get_devices()` | Fetch network devices | list[dict] |
| `get_health()` | Fetch health status | list[dict] |
| `get_system_stats()` | Aggregate system stats | dict |

**Session Management**:
- Cookie-based authentication
- Automatic session refresh on 401
- Retry logic for transient failures

### `sensor.py` - Sensor Platform

**Purpose**: Create and manage sensor entities

**Entity Types**:
- Network statistics (clients, speeds, latency)
- System resources (CPU, memory, uptime)
- Data counters (upload/download totals)

**Architecture Pattern**: CoordinatorEntity
- Inherits from Home Assistant's CoordinatorEntity
- Automatically updates when coordinator refreshes
- Efficient - no per-entity API calls

### `device_tracker.py` - Device Tracking

**Purpose**: Track network client presence

**Features**:
- Dynamic entity creation (new devices auto-discovered)
- Rich attributes (IP, MAC, signal, bandwidth, etc.)
- Away threshold (5 minutes default)
- Per-device information

**Entity Management**:
```python
Coordinator Update → Parse Clients → Create/Update Trackers
                                    → Mark Away if Last Seen > Threshold
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Home Assistant Core                       │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────┐
│                  Integration Entry                             │
│  ┌──────────────────────────────────────────────────────┐    │
│  │         DataUpdateCoordinator                         │    │
│  │  - Fetches data every 30 seconds                     │    │
│  │  - Handles errors and retries                        │    │
│  │  - Notifies all entities on update                   │    │
│  └──────────────┬───────────────────────────────────────┘    │
│                 │                                              │
│                 ▼                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │           UniFi Client                                │    │
│  │  - Manages authentication                            │    │
│  │  - Makes API requests                                │    │
│  │  - Parses responses                                  │    │
│  └──────────────┬───────────────────────────────────────┘    │
└─────────────────┼───────────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────────────┐
│                     UniFi API                                   │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐           │
│  │ /stat/sta  │  │/stat/device │  │ /stat/health │           │
│  │  Clients   │  │  Devices    │  │   Health     │           │
│  └────────────┘  └─────────────┘  └──────────────┘           │
└────────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────────────┐
│                    UDM Pro Max                                  │
└────────────────────────────────────────────────────────────────┘
```

## Coordinator Pattern

### Why Use a Coordinator?

1. **Efficiency**: Single API call updates all entities
2. **Rate Limiting**: Prevents excessive API requests
3. **Error Handling**: Centralized error management
4. **Resource Management**: Reduced network and CPU usage

### Coordinator Implementation

```python
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
        raise UpdateFailed(f"Error: {err}") from err

coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=DOMAIN,
    update_method=async_update_data,
    update_interval=SCAN_INTERVAL,
)
```

### Entity Access to Data

```python
class UniFiNetworkProSensor(CoordinatorEntity, SensorEntity):
    @property
    def native_value(self):
        # Access coordinator data
        return self.coordinator.data.get("stats", {}).get("cpu_usage", 0)
```

## Authentication Flow

```
┌─────────────┐
│   Startup   │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  POST /login     │──── Success ────┐
│  with creds      │                 │
└──────────────────┘                 │
       │                              │
       │ Failure                      │
       ▼                              ▼
┌──────────────────┐         ┌──────────────────┐
│  Raise Error     │         │  Store Session   │
│  (ConfigEntry    │         │  Cookie          │
│   NotReady)      │         └─────────┬────────┘
└──────────────────┘                   │
                                       ▼
                            ┌──────────────────┐
                            │  Make API        │
                            │  Requests        │
                            └─────────┬────────┘
                                      │
                            ┌─────────┴─────────┐
                            │                   │
                       200 OK              401 Unauthorized
                            │                   │
                            ▼                   ▼
                     ┌─────────────┐   ┌──────────────────┐
                     │ Return Data │   │ Auto Re-login    │
                     └─────────────┘   │ Retry Request    │
                                       └──────────────────┘
```

## Entity State Management

### Sensor Entities

Sensors use descriptors for clean, maintainable code:

```python
@dataclass
class UniFiSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[dict], any] = None

SENSOR_DESCRIPTIONS = (
    UniFiSensorEntityDescription(
        key="connected_clients",
        name="Connected Clients",
        value_fn=lambda data: data.get("stats", {}).get("connected_clients", 0),
    ),
    # ... more sensors
)
```

### Device Tracker Entities

Dynamic creation based on network clients:

```python
# New client detected
if mac not in tracked_devices:
    new_entity = UniFiNetworkDevice(coordinator, entry, client)
    async_add_entities([new_entity])
```

### State Updates

All entities update automatically when coordinator refreshes:

```
Coordinator Update → CoordinatorEntity.async_write_ha_state()
                   → Entity properties recalculated
                   → HA state machine updated
```

## Error Handling Strategy

### Levels of Error Handling

1. **Client Level** (`unifi_client.py`):
   - Network timeouts
   - HTTP errors
   - JSON parsing errors
   - Session expiry

2. **Coordinator Level** (`__init__.py`):
   - UpdateFailed exception on errors
   - Marks entities as unavailable
   - Logs errors for debugging

3. **Entity Level**:
   - Graceful degradation
   - Default values on missing data
   - Available property based on coordinator status

### Example Error Flow

```python
try:
    data = await client.get_clients()
except aiohttp.ClientError:
    # Client level: log and return empty
    _LOGGER.error("Network error")
    return []

# Coordinator level
try:
    return await async_update_data()
except Exception as err:
    # Raise UpdateFailed - marks entities unavailable
    raise UpdateFailed(f"Error: {err}") from err
```

## Performance Considerations

### Update Interval

Default: 30 seconds

**Rationale**:
- Balance between real-time data and API load
- UniFi Controller can handle this rate comfortably
- Most network changes visible within 30 seconds

**Customization**:
```python
# In __init__.py
SCAN_INTERVAL = timedelta(seconds=60)  # Slower updates
SCAN_INTERVAL = timedelta(seconds=15)  # Faster updates (not recommended)
```

### Memory Usage

**Per Device**:
- Sensor entities: ~12 entities × 1KB = 12KB
- Device trackers: ~1 entity per client × 2KB

**Example Network**:
- 50 devices = ~100KB of entity data
- Negligible impact on Home Assistant

### Network Usage

**Per Update Cycle**:
- 3 API requests (clients, devices, health)
- ~50KB total data transfer
- Minimal bandwidth impact

**Daily Bandwidth**:
- 2,880 update cycles (30s interval)
- ~144MB per day

## Security Architecture

### Authentication

- No credentials stored in entities
- Session cookies stored in memory only
- Automatic cleanup on unload

### Network Security

- HTTPS only (can disable cert verification for self-signed)
- No data sent outside local network
- No cloud dependencies

### Best Practices

1. Use strong UniFi passwords
2. Keep Home Assistant updated
3. Use firewall rules to restrict access
4. Enable SSL verification in production
5. Use dedicated service account (not owner)

## Extension Points

### Adding New Sensors

1. Add sensor description to `sensor.py`:
```python
UniFiSensorEntityDescription(
    key="new_metric",
    name="New Metric",
    value_fn=lambda data: data.get("stats", {}).get("new_metric", 0),
)
```

2. Update `unifi_client.get_system_stats()` to include data:
```python
stats["new_metric"] = device.get("new_field", 0)
```

### Adding Device Attributes

Update `device_tracker.py` in `extra_state_attributes`:
```python
if "new_field" in self._client_data:
    attributes["new_attribute"] = self._client_data["new_field"]
```

### Custom API Endpoints

Add new methods to `unifi_client.py`:
```python
async def get_custom_data(self) -> dict:
    return await self._make_request("/custom/endpoint")
```

## Testing Considerations

### Manual Testing

1. **API Client**: Test with different UDM models
2. **Error Handling**: Disconnect network, wrong credentials
3. **Performance**: Large networks (100+ devices)
4. **Long-running**: 24+ hour stability tests

### Automated Testing

```python
# Example unit test structure
def test_client_login():
    client = UniFiClient(...)
    result = await client.login()
    assert result == True

def test_sensor_values():
    coordinator = ...
    sensor = UniFiNetworkProSensor(coordinator, ...)
    assert sensor.native_value is not None
```

## Deployment Architecture

### Typical Homelab Setup

```
┌──────────────────────────────────────────────────────────┐
│                     Home Network                          │
│                                                            │
│  ┌──────────────┐         ┌──────────────────────┐      │
│  │ UDM Pro Max  │◄───────►│  Home Assistant      │      │
│  │ 192.168.1.1  │  HTTPS  │  192.168.1.10        │      │
│  │              │  :443   │  (Docker/VM/OS)      │      │
│  └──────┬───────┘         └──────────────────────┘      │
│         │                                                 │
│         │ Manages                                         │
│         ▼                                                 │
│  ┌─────────────────────────────────────────────┐        │
│  │  Network Devices (APs, Switches, Clients)   │        │
│  └─────────────────────────────────────────────┘        │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

### Docker Compose Example

```yaml
services:
  homeassistant:
    image: homeassistant/home-assistant:latest
    volumes:
      - ./config:/config
      - ./custom_components:/config/custom_components
    network_mode: host
    environment:
      - TZ=America/Los_Angeles
```

### Resource Requirements

**Minimum**:
- CPU: Negligible (~0.1% on modern systems)
- Memory: ~10MB
- Storage: ~5MB for integration files
- Network: ~144MB/day bandwidth

**Recommended**:
- Stable network connection to UDM
- Home Assistant on same LAN as UDM
- Wired connection preferred over WiFi

## Troubleshooting Architecture

### Debug Logging

Enable in `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.unifi_network_pro: debug
```

### Log Analysis

| Log Pattern | Meaning | Action |
|-------------|---------|--------|
| "Successfully logged in" | Auth OK | None |
| "Session expired" | Re-auth triggered | Normal, monitor if frequent |
| "Connection timeout" | Network issue | Check connectivity |
| "API request failed" | API error | Check UDM status |

### Metrics to Monitor

1. Update success rate (should be >99%)
2. Session refresh frequency (every 30+ minutes normal)
3. API response time (<500ms typical)
4. Entity availability (should be 100%)

## Future Enhancements

### Potential Features

1. **WebSocket Support**: Real-time updates instead of polling
2. **Port Statistics**: Per-port traffic monitoring
3. **Historical Graphs**: Built-in trend analysis
4. **Alerts**: Native notifications for events
5. **DPI Data**: Deep packet inspection statistics
6. **Multi-Site**: Support multiple UniFi sites
7. **Services**: Expose UniFi actions as HA services

### Scalability Improvements

1. Selective device tracking (filter by criteria)
2. Configurable update intervals per entity type
3. Batch API requests for large networks
4. Local caching of static data

## References

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Data Update Coordinator](https://developers.home-assistant.io/docs/integration_fetching_data)
- [Config Flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)
- [Entity Descriptions](https://developers.home-assistant.io/docs/core/entity)
