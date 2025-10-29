# UniFi Network Pro - Home Assistant Integration

A comprehensive Home Assistant custom integration for monitoring and managing Ubiquiti UniFi network devices, specifically optimized for the UDM Pro Max.

## Features

- **Real-time Network Monitoring**: Track network performance metrics including upload/download speeds, latency, and data usage
- **Device Tracking**: Automatically discover and track all devices connected to your network
- **System Monitoring**: Monitor UDM Pro Max CPU usage, memory usage, and uptime
- **Rich Entity Support**: Provides sensors and device trackers with comprehensive attributes
- **Easy Configuration**: User-friendly config flow through the Home Assistant UI
- **HACS Compatible**: Easy installation and updates through HACS

## Sensors Provided

The integration creates the following sensors:

### Network Statistics
- **Connected Clients**: Number of devices currently connected to the network
- **WAN IP Address**: Your public IP address
- **WAN Download Speed**: Current download speed (Mbps)
- **WAN Upload Speed**: Current upload speed (Mbps)
- **WAN Latency**: Network latency in milliseconds
- **WAN Download Total**: Total data downloaded via WAN (bytes)
- **WAN Upload Total**: Total data uploaded via WAN (bytes)
- **LAN Download Total**: Total data downloaded via LAN (bytes)
- **LAN Upload Total**: Total data uploaded via LAN (bytes)

### System Resources
- **CPU Usage**: UDM Pro Max CPU usage percentage
- **Memory Usage**: UDM Pro Max memory usage percentage
- **Uptime**: System uptime in seconds

## Device Trackers

Each network client is automatically discovered and added as a device tracker entity with the following attributes:

- MAC address
- IP address
- Hostname
- Connection type (wired/wireless)
- WiFi network name (for wireless devices)
- Signal strength (for wireless devices)
- Upload/download bytes
- Connection uptime
- Access point information
- WiFi channel

## Screenshots

(Add screenshots of your dashboard here)

## Requirements

- Home Assistant 2023.1 or newer
- Ubiquiti UDM Pro Max (or other UniFi Dream Machine)
- Local network access to your UniFi controller
- UniFi controller credentials (username and password)

## Installation

### Method 1: HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/yourusername/unifi_network_pro`
6. Select category "Integration"
7. Click "Add"
8. Search for "UniFi Network Pro" in HACS
9. Click "Download"
10. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from the releases page
2. Extract the contents
3. Copy the `custom_components/unifi_network_pro` directory to your Home Assistant's `custom_components` directory
4. If the `custom_components` directory doesn't exist, create it in your Home Assistant configuration directory
5. Restart Home Assistant

## Configuration

### Step 1: Add Integration

1. In Home Assistant, go to **Settings** > **Devices & Services**
2. Click the **+ ADD INTEGRATION** button
3. Search for "UniFi Network Pro"
4. Click on the integration to start the setup

### Step 2: Enter Connection Details

You'll be prompted to enter:

- **Host**: The IP address or hostname of your UDM Pro Max (e.g., `192.168.1.1` or `unifi.local`)
- **Username**: Your UniFi controller username (typically the owner account)
- **Password**: Your UniFi controller password
- **Site ID**: The site ID (default is "default" for most installations)
- **Verify SSL**: Whether to verify SSL certificates (leave unchecked for self-signed certificates)

### Step 3: Complete Setup

- Click **Submit**
- The integration will connect to your UniFi controller and validate credentials
- Once successful, all sensors and device trackers will be automatically created

## Dashboard Configuration

Two example dashboard configurations are provided:

### Basic Dashboard

Located at `examples/dashboard_basic.yaml`, this provides a simple, clean interface showing:
- Network status overview
- Speed gauges
- Data usage statistics
- Connected devices list

To use:
1. Copy the contents of `examples/dashboard_basic.yaml`
2. In Home Assistant, go to your Lovelace dashboard
3. Click the three dots menu > "Edit Dashboard"
4. Click "Raw configuration editor"
5. Paste the YAML configuration
6. Click "Save"

### Advanced Dashboard

Located at `examples/dashboard_advanced.yaml`, this provides a comprehensive monitoring interface with:
- System resource graphs
- Network speed trends
- Historical data
- Device tracking
- Custom styling

**Requirements for Advanced Dashboard:**
- mini-graph-card (HACS)
- bar-card (HACS)
- button-card (HACS)

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## API Reference

See [API.md](API.md) for details on the UniFi API endpoints used by this integration.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details about the integration's structure.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## Support

If you encounter issues:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search existing [GitHub Issues](https://github.com/yourusername/unifi_network_pro/issues)
3. Create a new issue with:
   - Home Assistant version
   - Integration version
   - UDM Pro Max firmware version
   - Detailed description of the issue
   - Relevant logs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the Home Assistant community
- Ubiquiti for the UniFi product line
- Contributors and testers

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by Ubiquiti Inc.
