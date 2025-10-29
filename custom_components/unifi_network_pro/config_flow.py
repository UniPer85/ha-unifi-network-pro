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

from .const import CONF_SITE_ID, DEFAULT_SITE_ID, DOMAIN
from .unifi_client import UniFiClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_SITE_ID, default=DEFAULT_SITE_ID): str,
        vol.Optional(CONF_VERIFY_SSL, default=False): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    This function will wait up to 60 seconds for login to complete,
    allowing time for 2FA approval via Unifi Verify app.
    """
    host = data[CONF_HOST]
    if not host.startswith("http"):
        host = f"https://{host}"
        data[CONF_HOST] = host

    session = async_get_clientsession(hass, verify_ssl=data.get(CONF_VERIFY_SSL, False))
    client = UniFiClient(
        host,
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
        session,
        data.get(CONF_VERIFY_SSL, False),
    )

    if CONF_SITE_ID in data:
        client.site_id = data[CONF_SITE_ID]

    try:
        _LOGGER.info("Attempting to connect to UniFi controller...")
        _LOGGER.info("If you have 2FA enabled, please approve the login on your Unifi Verify app within 60 seconds")

        login_success = await client.login(timeout=60)  # 60 second timeout for 2FA
        if not login_success:
            raise ValueError("Login failed - check credentials or 2FA approval")
    except Exception as err:
        _LOGGER.error("Connection failed: %s", err)
        raise

    # Test API access
    try:
        await client.get_clients()
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
