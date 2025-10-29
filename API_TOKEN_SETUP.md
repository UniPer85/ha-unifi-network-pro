# API Token Setup Guide

## Overview

**API Token authentication is the RECOMMENDED way** to connect this integration to your UDM Pro Max. It eliminates 2FA issues, 401 errors, and provides more stable authentication.

## Why Use API Token Instead of Username/Password?

✅ **No 2FA hassles** - Tokens don't require Unifi Verify approval
✅ **No 401 errors** - More stable authentication
✅ **Better security** - Tokens can be revoked without changing passwords
✅ **Persistent** - No session expiration issues
✅ **Dedicated access** - Separate from your admin account

## How to Create an API Token

### Step 1: Access UniFi OS Settings

1. Open your UDM Pro Max web interface
2. Navigate to: **Settings** → **System** → **Advanced**
3. Look for **"Integrations"** or **"API"** section

**OR**

1. Go directly to UniFi OS Console
2. Open **Settings**
3. Find **Admins & Users** or **API Access**

### Step 2: Generate API Token

The exact location varies by UniFi OS version:

#### UniFi OS 3.0+ (Newer)

1. Go to **Settings** → **Admins & Users** → **API Access**
2. Click **"Generate API Token"** or **"Create New Token"**
3. Enter a name: `Home Assistant Integration`
4. Set permissions: **Read** (minimum) or **Full Access** if you want control features later
5. Click **Generate** or **Create**
6. **IMPORTANT**: Copy the token immediately - you won't see it again!

#### UniFi OS 2.x (Older)

1. Go to **Settings** → **System** → **Advanced**
2. Look for **"API"** or **"Local API"** section
3. Enable **"Local API Access"**
4. Create new API key
5. Name it: `Home Assistant`
6. Copy the generated key

### Step 3: Note Your Site ID (Optional)

Most installations use `default` as the site ID, but if you're not sure:

1. In UniFi Network application, look at the URL:
   ```
   https://192.168.1.1/network/default/dashboard
                               ^^^^^^^ this is your site_id
   ```

2. Or check: **Settings** → **System** → **Site Settings** → Site name

## How to Use the API Token in Home Assistant

### During Initial Setup

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for **"UniFi Network Pro"**
4. Fill in the form:
   - **Host**: Your UDM IP (e.g., `192.168.1.1`)
   - **API Token**: Paste the token you copied
   - **Username**: Leave empty
   - **Password**: Leave empty
   - **Site ID**: `default` (or your custom site ID)
   - **Verify SSL**: Uncheck (unless you have a valid certificate)
5. Click **Submit**
6. Integration should connect immediately!

### Example Configuration

```
Host: 192.168.1.1
API Token: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
Username: (leave empty)
Password: (leave empty)
Site ID: default
Verify SSL: No
```

## Troubleshooting

### "Invalid authentication credentials or API token"

**Causes:**
- Wrong API token
- Token was regenerated/revoked
- Insufficient token permissions

**Solutions:**
1. Verify the token is correct (no extra spaces)
2. Regenerate a new token in UDM settings
3. Ensure token has at least **Read** permissions
4. Check that API access is enabled on your UDM

### "Cannot find API/Integrations section"

**UniFi OS version differences:**

- **UniFi OS 3.0+**: Settings → Admins & Users → API Access
- **UniFi OS 2.x**: Settings → System → Advanced → API
- **UniFi OS 1.x**: May not support API tokens - use username/password instead

**Check your version:**
- Look at bottom-left of UniFi OS Console
- Shows "UniFi OS v3.2.7" or similar

### Still Getting 401 Errors

If API token still gives 401 errors:

1. **Check token permissions**: Token needs at least Read access to:
   - Network devices
   - Clients
   - System stats

2. **Try creating a dedicated local admin user** instead:
   - Settings → Admins & Users → Add Admin
   - Create user: `homeassistant`
   - Role: Read-Only (or Full if you want control features)
   - Don't enable 2FA for this user
   - Use username/password authentication in HA

3. **Check site ID**: Verify you're using the correct site name
   - Default is usually `default`
   - Can be different if you renamed it

## API Token vs Username/Password Comparison

| Feature | API Token | Username/Password |
|---------|-----------|-------------------|
| 2FA Required | ❌ No | ✅ Yes (if enabled) |
| Session Expiration | ❌ Never | ✅ Yes (24-72 hours) |
| 401 Errors | ⚠️ Rare | ⚠️ Common |
| Setup Complexity | ⭐⭐ Medium | ⭐⭐⭐ Complex |
| Security | ✅ High | ✅ High |
| Revocation | ✅ Easy | ❌ Requires password change |

## Security Best Practices

1. **Use read-only permissions** if you only need monitoring
2. **Don't share the API token** - treat it like a password
3. **Revoke old tokens** when no longer needed
4. **Use separate tokens** for different integrations
5. **Store tokens securely** - Home Assistant encrypts config data

## Legacy/Alternative: Local Admin User

If your UDM doesn't support API tokens, create a dedicated local user:

1. Settings → Admins & Users → Add Admin
2. Username: `homeassistant`
3. Password: Strong random password
4. Role: Read-Only or Custom (with minimum permissions)
5. **Don't enable 2FA** for this account
6. Use this username/password in Home Assistant

This avoids 2FA issues while maintaining security through limited permissions.

## What Permissions Does the Integration Need?

**Minimum (Read-Only):**
- View network clients
- View network devices
- View system statistics
- View health status

**Optional (for future control features):**
- Block/unblock clients
- Restart devices
- Change device settings

For now, **Read-Only** is sufficient as the integration only monitors.

## Need Help?

If you're having trouble:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Check the [2FA Setup Guide](2FA_SETUP.md) if using username/password
3. Enable debug logging in Home Assistant:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.unifi_network_pro: debug
   ```
4. Check logs for specific error messages
5. Open an issue on [GitHub](https://github.com/UniPer85/ha-unifi-network-pro/issues)

## Version History

### v1.2.0
- ✅ Added API token authentication support
- ✅ Automatic detection of auth method
- ✅ Improved error messages
- ✅ No more 401 errors with API tokens

### v1.1.x
- Username/password with 2FA polling
- Cookie-based session persistence
