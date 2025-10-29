# Installation Guide - UniFi Network Pro

This guide provides detailed step-by-step instructions for installing and configuring the UniFi Network Pro integration for Home Assistant.

## Prerequisites

Before you begin, ensure you have:

1. **Home Assistant** running version 2023.1 or newer
2. **UDM Pro Max** or compatible UniFi Dream Machine
3. **Network Access** to your UniFi controller
4. **Controller Credentials** - username and password with admin access
5. **SSH Access** (optional, for manual installation method)

## Installation Methods

### Option 1: HACS Installation (Recommended)

HACS (Home Assistant Community Store) is the easiest way to install and keep the integration updated.

#### Step 1: Install HACS

If you don't have HACS installed:

1. Visit https://hacs.xyz/docs/setup/download
2. Follow the installation instructions
3. Restart Home Assistant
4. Complete HACS setup through the UI

#### Step 2: Add Custom Repository

1. Open Home Assistant
2. Navigate to **HACS** in the sidebar
3. Click on **Integrations**
4. Click the **three dots** (⋮) in the top right corner
5. Select **Custom repositories**
6. In the dialog:
   - Repository: `https://github.com/yourusername/unifi_network_pro`
   - Category: `Integration`
7. Click **Add**

#### Step 3: Install the Integration

1. In HACS Integrations, search for "UniFi Network Pro"
2. Click on the integration
3. Click **Download**
4. Select the latest version
5. Click **Download** again to confirm

#### Step 4: Restart Home Assistant

1. Go to **Settings** > **System**
2. Click **Restart** in the top right
3. Confirm the restart
4. Wait for Home Assistant to come back online (typically 1-2 minutes)

### Option 2: Manual Installation

For advanced users or if HACS is not available.

#### Step 1: Download the Integration

Download the latest release:

```bash
cd /tmp
wget https://github.com/yourusername/unifi_network_pro/releases/latest/download/unifi_network_pro.zip
unzip unifi_network_pro.zip
```

Or clone from Git:

```bash
cd /tmp
git clone https://github.com/yourusername/unifi_network_pro.git
```

#### Step 2: Copy to Home Assistant

Copy the integration to your Home Assistant installation:

```bash
# If using Docker
docker cp /tmp/unifi_network_pro/custom_components/unifi_network_pro /path/to/homeassistant/config/custom_components/

# If using Home Assistant OS (via SSH add-on)
cp -r /tmp/unifi_network_pro/custom_components/unifi_network_pro /config/custom_components/

# If using supervised installation
cp -r /tmp/unifi_network_pro/custom_components/unifi_network_pro /usr/share/hassio/homeassistant/custom_components/
```

#### Step 3: Verify File Structure

Your file structure should look like:

```
config/
└── custom_components/
    └── unifi_network_pro/
        ├── __init__.py
        ├── config_flow.py
        ├── const.py
        ├── device_tracker.py
        ├── manifest.json
        ├── sensor.py
        ├── strings.json
        ├── unifi_client.py
        └── translations/
            └── en.json
```

#### Step 4: Set Permissions (if needed)

```bash
chmod -R 755 /config/custom_components/unifi_network_pro
chown -R homeassistant:homeassistant /config/custom_components/unifi_network_pro
```

#### Step 5: Restart Home Assistant

Restart via UI or command line:

```bash
# Via Home Assistant CLI
ha core restart

# Or restart the container/service depending on your installation type
```

## Configuration

### Step 1: Prepare UniFi Controller Information

Before configuring, gather the following information:

1. **Controller IP/Hostname**:
   - Find your UDM Pro Max IP address (e.g., `192.168.1.1`)
   - Or use the hostname if configured (e.g., `unifi.local`)

2. **Admin Credentials**:
   - Username (the owner account or an admin user)
   - Password

3. **Site ID** (usually "default"):
   - Log into your UniFi controller web interface
   - Check the URL: `https://192.168.1.1/network/default/dashboard`
   - The word after `/network/` is your site ID

### Step 2: Add Integration via UI

1. In Home Assistant, navigate to:
   **Settings** > **Devices & Services**

2. Click the **+ ADD INTEGRATION** button (bottom right)

3. Search for "UniFi Network Pro"

4. Click on "UniFi Network Pro" in the search results

### Step 3: Enter Configuration Details

Fill in the configuration form:

| Field | Description | Example |
|-------|-------------|---------|
| **Host** | IP address or hostname of UDM Pro Max | `192.168.1.1` or `https://192.168.1.1` |
| **Username** | UniFi controller username | `admin` |
| **Password** | UniFi controller password | `your_password` |
| **Site ID** | Site identifier (usually "default") | `default` |
| **Verify SSL** | Check if using valid SSL cert | Unchecked (for most users) |

### Step 4: Submit and Verify

1. Click **Submit**

2. The integration will:
   - Connect to your UniFi controller
   - Authenticate with the provided credentials
   - Test API access
   - Discover devices

3. If successful, you'll see:
   - A new device: "UniFi Network"
   - Multiple sensor entities created
   - Device tracker entities for connected clients

4. If unsuccessful, see the error messages:
   - **cannot_connect**: Check IP address and network connectivity
   - **invalid_auth**: Verify username and password
   - **unknown**: Check logs for details

### Step 5: Verify Entities

Check that entities were created:

1. Go to **Settings** > **Devices & Services**
2. Find "UniFi Network Pro" integration
3. Click on it to see the device
4. Click on "UniFi Network" device
5. Verify you see entities like:
   - `sensor.unifi_network_connected_clients`
   - `sensor.unifi_network_cpu_usage`
   - `sensor.unifi_network_wan_download_speed`
   - And device trackers for your network clients

## Post-Installation Steps

### 1. Customize Entity Names

Rename entities for easier identification:

1. Click on an entity
2. Click the settings icon (gear)
3. Update the "Name" field
4. Click "Update"

### 2. Configure Dashboard

See the example dashboards:
- `examples/dashboard_basic.yaml` - Simple layout
- `examples/dashboard_advanced.yaml` - Full-featured (requires custom cards)

### 3. Set Up Automations

Example automation to notify when new devices connect:

```yaml
automation:
  - alias: "Notify on new device"
    trigger:
      - platform: state
        entity_id: sensor.unifi_network_connected_clients
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
    action:
      - service: notify.mobile_app
        data:
          message: "New device connected to network!"
```

### 4. Enable Debug Logging (Optional)

Add to `configuration.yaml` for troubleshooting:

```yaml
logger:
  default: info
  logs:
    custom_components.unifi_network_pro: debug
```

## Network Configuration

### Firewall Rules

Ensure Home Assistant can reach your UDM Pro Max:

1. In UniFi Network application:
2. Go to **Settings** > **Security** > **Firewall**
3. Create a rule to allow traffic from Home Assistant IP to UDM Pro Max on port 443

### VLAN Considerations

If Home Assistant is on a different VLAN:

1. Ensure routing is enabled between VLANs
2. Create firewall rules to allow HTTPS (443) traffic
3. Test connectivity: `ping <UDM_IP>` from Home Assistant

### SSL Certificate Issues

If you encounter SSL errors:

1. **Option A**: Disable SSL verification (leave "Verify SSL" unchecked)
2. **Option B**: Install a valid SSL certificate on your UDM Pro Max
3. **Option C**: Add UDM's self-signed cert to Home Assistant's trusted certificates

## Updating

### Via HACS

1. Open HACS
2. Go to Integrations
3. Find "UniFi Network Pro"
4. If an update is available, click "Update"
5. Restart Home Assistant

### Manual Update

1. Download the latest release
2. Replace the files in `custom_components/unifi_network_pro/`
3. Restart Home Assistant

## Uninstallation

### Step 1: Remove Integration

1. Go to **Settings** > **Devices & Services**
2. Find "UniFi Network Pro"
3. Click the three dots (⋮)
4. Select "Delete"
5. Confirm deletion

### Step 2: Remove Files (Optional)

```bash
rm -rf /config/custom_components/unifi_network_pro/
```

### Step 3: Restart Home Assistant

## Verification Checklist

After installation, verify:

- [ ] Integration appears in Devices & Services
- [ ] "UniFi Network" device is created
- [ ] Sensor entities are populated with data
- [ ] Device trackers show connected devices
- [ ] Entities update regularly (every 30 seconds)
- [ ] No errors in Home Assistant logs
- [ ] Dashboard displays data correctly

## Next Steps

- [Configure a dashboard](README.md#dashboard-configuration)
- [Set up automations](EXAMPLES.md#automation-examples)
- [Troubleshoot issues](TROUBLESHOOTING.md)
- [Read the API documentation](API.md)

## Getting Help

If you encounter issues during installation:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Enable debug logging and check logs
3. Verify network connectivity to UDM Pro Max
4. Search [GitHub Issues](https://github.com/yourusername/unifi_network_pro/issues)
5. Create a new issue with installation details
