"""Config flow for UniFi Network Pro integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_TOKEN, CONF_SITE_ID, DEFAULT_SITE_ID, DOMAIN
from .unifi_client import UniFiClient

_LOGGER = logging.getLogger(__name__)

# Schema for username/password authentication
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Optional(CONF_API_TOKEN): str,
        vol.Optional(CONF_SITE_ID, default=DEFAULT_SITE_ID): str,
        vol.Optional(CONF_VERIFY_SSL, default=False): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Supports both username/password and API token authentication.
    """
    host = data[CONF_HOST]
    if not host.startswith("http"):
        host = f"https://{host}"
        data[CONF_HOST] = host

    # Check if using API token or username/password
    api_token = data.get(CONF_API_TOKEN)
    username = data.get(CONF_USERNAME)
    password = data.get(CONF_PASSWORD)

    if not api_token and (not username or not password):
        raise ValueError("Must provide either API token OR username and password")

    session = async_get_clientsession(hass, verify_ssl=data.get(CONF_VERIFY_SSL, False))

    if api_token:
        _LOGGER.info("Attempting to connect using API token...")
        client = UniFiClient(
            host,
            session=session,
            verify_ssl=data.get(CONF_VERIFY_SSL, False),
            api_token=api_token,
        )
    else:
        _LOGGER.info("Attempting to connect using username/password...")
        _LOGGER.info("If you have 2FA enabled, please approve the login on your Unifi Verify app within 60 seconds")
        client = UniFiClient(
            host,
            username=username,
            password=password,
            session=session,
            verify_ssl=data.get(CONF_VERIFY_SSL, False),
        )

    if CONF_SITE_ID in data:
        client.site_id = data[CONF_SITE_ID]

    try:
        if not api_token:
            login_success = await client.login(timeout=60)  # 60 second timeout for 2FA
            if not login_success:
                raise ValueError("Login failed - check credentials or 2FA approval")
    except Exception as err:
        _LOGGER.error("Connection failed: %s", err)
        raise

    # Test API access
    try:
        clients = await client.get_clients()
        _LOGGER.info("Successfully connected! Found %d clients", len(clients))
    except Exception as err:
        _LOGGER.error("API access test failed: %s", err)
        raise

    return {"title": f"UniFi Network ({host})"}


class UniFiNetworkProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for UniFi Network Pro."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except ValueError:
                errors["base"] = "invalid_auth"
            except aiohttp.ClientConnectorError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
