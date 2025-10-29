# 2FA Authentication Guide

## Overview

This integration now fully supports **Unifi Verify 2FA authentication** with persistent session management. You will only need to approve the login once, and the integration will maintain your session across Home Assistant restarts.

## Features

✅ **Extended 60-second timeout** - Plenty of time to approve login on your mobile device
✅ **Persistent sessions** - Login once, stay authenticated across HA restarts
✅ **Automatic re-authentication** - Seamlessly re-login if session expires
✅ **Secure cookie storage** - Session tokens stored securely in HA storage

## How It Works

### Initial Setup (First Time)

1. **Add the Integration**
   - Go to Settings → Devices & Services → Add Integration
   - Search for "UniFi Network Pro"
   - Enter your UDM Pro Max details:
     - Host IP (e.g., `192.168.1.1` or `https://192.168.1.1`)
     - Username
     - Password
     - Site ID (default: `default`)

2. **Approve 2FA Request**
   - After clicking Submit, check your **Unifi Verify app** on your mobile device
   - You have **60 seconds** to approve the login request
   - Approve the request

3. **Integration Complete**
   - Once approved, the integration will connect
   - Your session will be saved automatically

### Session Persistence

**After initial setup:**
- Session cookies are stored in: `.storage/unifi_network_pro/{entry_id}_cookies.json`
- Home Assistant will reuse these cookies on restart
- **No need to approve 2FA again** unless session expires (typically 24-72 hours)

### When Session Expires

If your session expires (rare), the integration will:
1. Detect the expired session (401 error)
2. Automatically attempt to re-login
3. Send a new 2FA request to your Unifi Verify app
4. Wait 60 seconds for approval
5. Continue operation once approved

You'll see this in the logs:
```
Session expired (401), attempting to re-login
If you have 2FA enabled, please approve the login on your Unifi Verify app
```

## Troubleshooting

### "Login timeout after 60s"

**Cause**: You didn't approve the 2FA request in time

**Solution**:
1. Go to Settings → Devices & Services
2. Find "UniFi Network Pro" integration
3. Click "Configure" or "Reload"
4. Check your Unifi Verify app and approve within 60 seconds

### "Login failed - check credentials or 2FA approval"

**Causes**:
- Wrong username/password
- 2FA request denied
- 2FA request expired

**Solution**:
1. Verify your credentials are correct
2. Check Unifi Verify app for any pending/denied requests
3. Try again and approve the request promptly

### Session Keeps Expiring

**Cause**: UniFi controller configured with very short session timeout

**Solution**:
1. Log into your UDM Pro Max web interface
2. Go to Settings → System → Advanced
3. Increase "Session Timeout" to 24+ hours
4. Or: Disable 2FA for the local user (less secure)

### Want to Force Re-authentication?

Delete the stored session cookies:
```bash
rm /config/.storage/unifi_network_pro/*_cookies.json
```
Then restart Home Assistant.

## Alternative: Local User Without 2FA

If you prefer not to use 2FA for Home Assistant:

1. **Create a Local-Only User on UDM**
   - Log into UniFi Network web interface
   - Go to Settings → System → Admins
   - Add new admin user
   - Username: `homeassistant` (or your choice)
   - Password: Strong password
   - Role: Administrator (or View Only if you only need monitoring)
   - **Don't enable 2FA for this user**

2. **Use Local User in Home Assistant**
   - Configure the integration with the new username
   - No 2FA approval needed
   - Sessions still persist across restarts

## Logs to Monitor

Enable debug logging to see authentication details:

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.unifi_network_pro: debug
    custom_components.unifi_network_pro.unifi_client: debug
```

**Key log messages:**
- `Attempting login to UniFi controller (timeout: 60s)` - Login started
- `If you have 2FA enabled, please approve the login` - Check Unifi Verify app
- `Successfully logged in to UniFi controller` - Login successful
- `Saved N cookies to storage` - Session cookies saved
- `Loaded N cookies from storage` - Session restored from previous login
- `Session expired (401), attempting to re-login` - Auto re-authentication

## Security Notes

- Session cookies are stored in Home Assistant's `.storage` directory
- Files have restricted permissions (only accessible by HA)
- Cookies are cleared on logout or integration removal
- Consider using a dedicated local user without 2FA for maximum security

## Version History

### v1.1.0 (Current)
- ✅ Added 2FA support with 60-second timeout
- ✅ Persistent session management
- ✅ Automatic re-authentication on session expiry
- ✅ Secure cookie storage
- ✅ Helpful log messages for 2FA approval

### v1.0.0
- Initial release (no 2FA support)
