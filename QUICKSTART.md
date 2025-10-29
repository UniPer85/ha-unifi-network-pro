# Quick Start Guide

Get up and running with UniFi Network Pro in 5 minutes.

## Prerequisites

- Home Assistant 2023.1+
- UDM Pro Max or compatible UniFi device
- Admin credentials for your UniFi controller

## Installation (Choose One Method)

### Method 1: HACS (Easiest)

1. Open HACS in Home Assistant
2. Go to Integrations
3. Click ⋮ → Custom repositories
4. Add: `https://github.com/yourusername/unifi_network_pro`
5. Category: Integration
6. Search "UniFi Network Pro" and install
7. Restart Home Assistant

### Method 2: Manual

```bash
# Navigate to your Home Assistant config directory
cd /config

# Create custom_components if it doesn't exist
mkdir -p custom_components

# Copy the integration
cp -r /path/to/custom_components/unifi_network_pro custom_components/

# Restart Home Assistant
```

## Configuration (3 Steps)

### Step 1: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for "UniFi Network Pro"

### Step 2: Enter Details

Fill in the form:

```
Host: 192.168.1.1          (Your UDM IP)
Username: admin            (Your admin username)
Password: ********         (Your password)
Site ID: default          (Usually "default")
Verify SSL: □             (Unchecked for most users)
```

### Step 3: Done!

You should now see:
- 12 sensor entities
- Device tracker entities for all connected devices

## Verify It's Working

Check for these entities:

```
sensor.unifi_network_connected_clients
sensor.unifi_network_cpu_usage
sensor.unifi_network_wan_ip_address
device_tracker.{your_devices}
```

## Add a Dashboard

### Option 1: Basic Dashboard

1. Create a new dashboard
2. Copy contents from `examples/dashboard_basic.yaml`
3. Paste into dashboard YAML editor
4. Save

### Option 2: Advanced Dashboard

Requires HACS custom cards:
- mini-graph-card
- bar-card
- button-card

Then use `examples/dashboard_advanced.yaml`

## Common First-Time Issues

### "Cannot Connect"
- Verify UDM IP: `ping 192.168.1.1`
- Try with `https://` prefix: `https://192.168.1.1`
- Check firewall rules

### "Invalid Auth"
- Log into UniFi web UI with same credentials
- Use local account, not Ubiquiti cloud account
- Check for account lockout (wait 15 minutes)

### "Integration Not Found"
- Restart Home Assistant after installation
- Clear browser cache (Ctrl+F5)
- Check files are in `/config/custom_components/unifi_network_pro/`

## Next Steps

- [Read full documentation](README.md)
- [Configure automations](EXAMPLES.md)
- [Customize dashboard](examples/)
- [Troubleshoot issues](TROUBLESHOOTING.md)

## Get Help

- [GitHub Issues](https://github.com/yourusername/unifi_network_pro/issues)
- [Community Forum](https://community.home-assistant.io/)
- Enable debug logging (see TROUBLESHOOTING.md)

## Quick Reference

**Default Update Interval**: 30 seconds
**Platforms**: Sensor, Device Tracker
**API Port**: 443 (HTTPS)
**Supported Devices**: UDM, UDM Pro, UDM Pro Max, UDM SE
