# Troubleshooting Guide - UniFi Network Pro

This guide covers common issues and their solutions when using the UniFi Network Pro integration.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Connection Problems](#connection-problems)
- [Authentication Errors](#authentication-errors)
- [Entity Issues](#entity-issues)
- [Performance Problems](#performance-problems)
- [Dashboard Issues](#dashboard-issues)
- [Debug Logging](#debug-logging)

## Installation Issues

### Integration Not Showing in Available Integrations

**Symptoms**: Can't find "UniFi Network Pro" when adding a new integration.

**Solutions**:

1. **Verify Installation**:
   ```bash
   ls -la /config/custom_components/unifi_network_pro/
   ```
   Should show all integration files.

2. **Check File Permissions**:
   ```bash
   chmod -R 755 /config/custom_components/unifi_network_pro
   ```

3. **Clear Browser Cache**:
   - Press Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)
   - Or clear browser cache completely

4. **Restart Home Assistant**:
   ```bash
   ha core restart
   ```

5. **Check Logs**:
   Look for errors in Settings > System > Logs related to custom_components

### Module Import Errors

**Symptoms**: Errors about missing modules or imports in logs.

**Error Example**:
```
ModuleNotFoundError: No module named 'aiohttp'
```

**Solution**:
This shouldn't happen as aiohttp is a core dependency, but if it does:

1. Ensure Home Assistant is up to date
2. Restart Home Assistant
3. If using Docker, rebuild the container
4. Check that manifest.json includes required dependencies

## Connection Problems

### Cannot Connect to UniFi Controller

**Symptoms**: "Failed to connect to the UniFi controller" error during setup.

**Troubleshooting Steps**:

1. **Verify Controller Address**:
   ```bash
   ping <your_udm_ip>
   ```
   Ensure Home Assistant can reach the UDM Pro Max.

2. **Test HTTPS Access**:
   ```bash
   curl -k https://<your_udm_ip>
   ```
   Should return HTML or JSON response.

3. **Check Firewall Rules**:
   - Log into UniFi Network application
   - Go to Settings > Security > Firewall
   - Ensure Home Assistant's IP can access UDM on port 443

4. **VLAN Configuration**:
   - If on different VLANs, ensure inter-VLAN routing is enabled
   - Create firewall rules to allow traffic between VLANs

5. **Try Full URL**:
   Use `https://192.168.1.1` instead of just `192.168.1.1`

### SSL Certificate Errors

**Symptoms**: SSL verification errors in logs.

**Error Example**:
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions**:

1. **Disable SSL Verification** (Quick Fix):
   - During setup, uncheck "Verify SSL Certificate"
   - This is safe for local network use

2. **Install Valid Certificate** (Proper Fix):
   - Use Let's Encrypt on your UDM Pro Max
   - Or install a valid certificate from a trusted CA

3. **Add Self-Signed Cert to Home Assistant**:
   ```bash
   # Export cert from UDM
   openssl s_client -connect <udm_ip>:443 -showcerts > /tmp/unifi.crt

   # Copy to Home Assistant
   cp /tmp/unifi.crt /config/custom_certificates/
   ```

### Connection Timeouts

**Symptoms**: Integration setup times out or entities show "unavailable".

**Solutions**:

1. **Check Network Latency**:
   ```bash
   ping -c 10 <udm_ip>
   ```
   Should have low latency (<10ms for local network)

2. **Reduce Scan Interval**:
   Not recommended, but possible by editing `__init__.py`:
   ```python
   SCAN_INTERVAL = timedelta(seconds=60)  # Instead of 30
   ```

3. **Check UDM Load**:
   - High CPU/memory on UDM can cause slow API responses
   - Log into UDM and check system stats

## Authentication Errors

### Invalid Authentication Credentials

**Symptoms**: "Invalid authentication credentials" during setup.

**Solutions**:

1. **Verify Credentials**:
   - Log into UniFi web interface with same credentials
   - Ensure using the owner account or an admin user

2. **Check for Special Characters**:
   - Passwords with special characters might need escaping
   - Try changing password temporarily for testing

3. **Account Lockout**:
   - Too many failed attempts may lock the account
   - Wait 15 minutes and try again
   - Check UDM admin logs for lockout messages

4. **Local vs Cloud Account**:
   - Use local UniFi OS account, not Ubiquiti cloud account
   - Go to System > Users in UniFi OS to verify

### Session Expired Errors

**Symptoms**: Integration works initially but then shows "unavailable".

**Error Example**:
```
Session expired, attempting to re-login
```

**Solutions**:

1. This is normal behavior - the integration automatically re-authenticates
2. If it persists:
   - Check UDM logs for session issues
   - Verify Home Assistant time is synchronized (NTP)
   - Restart the integration

## Entity Issues

### Entities Not Showing Up

**Symptoms**: Integration configured but no entities created.

**Troubleshooting**:

1. **Check Integration Status**:
   - Go to Settings > Devices & Services
   - Click on "UniFi Network Pro"
   - Should show "1 device" and multiple entities

2. **Verify API Access**:
   Enable debug logging and check for API errors

3. **Check Site ID**:
   - Incorrect site ID will return no data
   - Default is "default"
   - Find yours in UniFi URL: `https://udm/network/{site_id}/`

### Device Trackers Not Updating

**Symptoms**: Device tracker entities show old status or don't update.

**Solutions**:

1. **Check Update Coordinator**:
   - Enable debug logging
   - Look for "Error communicating with UniFi" messages

2. **Verify Devices Are Active**:
   - Check in UniFi Network application
   - Ensure devices are actually connected

3. **MAC Address Issues**:
   - Some devices randomize MAC addresses
   - Disable MAC randomization on device WiFi settings

### Sensor Values Are Zero or Null

**Symptoms**: Sensors exist but show 0, null, or "unknown".

**Solutions**:

1. **Check Data Availability**:
   - Some metrics require UniFi telemetry to be enabled
   - Go to UniFi Settings > System > Advanced
   - Enable "Collect data for analytics and improvements"

2. **Wait for Speed Test**:
   - WAN speed sensors need a speed test to run
   - Manually trigger one in UniFi Settings > Internet

3. **Verify UDM Model**:
   - Some sensors are UDM-specific
   - Ensure your device reports as "udm" type

## Performance Problems

### High CPU Usage

**Symptoms**: Home Assistant CPU usage increased after adding integration.

**Solutions**:

1. **Increase Scan Interval**:
   Edit `__init__.py`:
   ```python
   SCAN_INTERVAL = timedelta(seconds=60)  # Default is 30
   ```

2. **Disable Unused Device Trackers**:
   - Go to each device tracker entity
   - Disable entities for devices you don't need to track

3. **Check Number of Clients**:
   - Large networks (100+ devices) may impact performance
   - Consider filtering device trackers by importance

### Slow Updates

**Symptoms**: Entities take a long time to update or lag behind reality.

**Solutions**:

1. **Check UDM Performance**:
   - Monitor UDM CPU/memory usage
   - Consider upgrading firmware if outdated

2. **Network Latency**:
   - Ensure Home Assistant has fast, stable network connection
   - Use wired connection if possible

3. **API Rate Limiting**:
   - UniFi may rate-limit API requests
   - Increase scan interval if making other API calls

## Dashboard Issues

### Graphs Not Showing Data

**Symptoms**: Dashboard cards show "No data" or empty graphs.

**Solutions**:

1. **Wait for Data Collection**:
   - Sensors need time to collect historical data
   - Wait at least 1 hour for graphs to populate

2. **Check Entity Names**:
   - Ensure dashboard YAML uses correct entity IDs
   - Entity IDs may be different if you customized names

3. **Enable Recorder**:
   Ensure recorder is configured in `configuration.yaml`:
   ```yaml
   recorder:
     purge_keep_days: 7
     include:
       domains:
         - sensor
         - device_tracker
   ```

### Custom Cards Not Working

**Symptoms**: Advanced dashboard shows errors or blank cards.

**Solutions**:

1. **Install Required Cards**:
   - mini-graph-card
   - bar-card
   - button-card

   Install via HACS > Frontend

2. **Check Card Configuration**:
   - Ensure YAML syntax is correct
   - Validate with YAML checker

3. **Clear Frontend Cache**:
   - Settings > System > Advanced
   - Click "Clear frontend cache"

## Debug Logging

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.unifi_network_pro: debug
    custom_components.unifi_network_pro.unifi_client: debug
    custom_components.unifi_network_pro.sensor: debug
    custom_components.unifi_network_pro.device_tracker: debug
```

Restart Home Assistant, then check logs:
- Settings > System > Logs
- Or: `/config/home-assistant.log`

### Useful Log Patterns

**Successful Connection**:
```
Successfully logged in to UniFi controller
```

**API Request**:
```
Making request to: https://192.168.1.1/proxy/network/api/s/default/stat/sta
```

**Session Expiry**:
```
Session expired, attempting to re-login
```

**Error Pattern**:
```
ERROR (MainThread) [custom_components.unifi_network_pro]
```

## Common Error Messages

### "Login failed"

**Cause**: Incorrect credentials or account locked.

**Fix**: Verify username/password, check for account lockout.

### "API access test failed"

**Cause**: Can login but can't access API endpoints.

**Fix**:
- Verify user has admin permissions
- Check site ID is correct
- Enable API access in UniFi settings

### "Error communicating with UniFi"

**Cause**: Network connectivity issue or UDM offline.

**Fix**:
- Check network connection
- Verify UDM is online and responsive
- Check firewall rules

### "Unable to parse JSON response"

**Cause**: UniFi API returned unexpected response.

**Fix**:
- Check UDM firmware version (update if old)
- Verify API endpoints haven't changed
- Enable debug logging to see raw response

## Getting Additional Help

If your issue isn't covered here:

1. **Enable Debug Logging**: Capture detailed logs
2. **Check GitHub Issues**: Search for similar problems
3. **Create New Issue**: Include:
   - Home Assistant version
   - Integration version
   - UDM firmware version
   - Relevant log entries
   - Steps to reproduce

## Advanced Troubleshooting

### Manual API Testing

Test API access manually:

```bash
# Login
curl -k -X POST https://<udm_ip>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpass","remember":true}' \
  -c cookies.txt

# Get clients
curl -k https://<udm_ip>/proxy/network/api/s/default/stat/sta \
  -b cookies.txt
```

Should return JSON with client data.

### Network Packet Capture

Use Wireshark or tcpdump to capture API traffic:

```bash
tcpdump -i any -s 0 -w /tmp/unifi.pcap host <udm_ip> and port 443
```

Analyze to see if requests are reaching UDM and responses are returning.

### Component Reload

Reload integration without restarting:

```bash
# Home Assistant CLI
ha core reload
```

Or through Developer Tools > YAML > YAML Configuration Reloading

## Prevention Tips

1. **Keep Firmware Updated**: Regularly update UDM and Home Assistant
2. **Monitor Logs**: Check logs weekly for warnings
3. **Backup Configuration**: Before making changes
4. **Test Network**: Verify network stability
5. **Document Changes**: Keep notes on customizations

## Known Issues

### Issue: Device tracker shows "away" immediately after connecting

**Status**: Known behavior

**Workaround**: Adjust `AWAY_THRESHOLD` in `device_tracker.py`

### Issue: WAN speed sensors require manual speed test

**Status**: UniFi API limitation

**Workaround**: Schedule regular speed tests or use automation

### Issue: Some advanced stats not available

**Status**: Depends on UDM model and firmware

**Workaround**: Check which stats your specific model supports
