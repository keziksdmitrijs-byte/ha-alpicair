"""Config flow for AlpicAir Modbus."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_CONNECTION_TYPE,
    CONNECTION_TCP,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE,
    DOMAIN,
)


class AlpicAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input['slave']}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
        schema = vol.Schema({
            vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Required(CONF_CONNECTION_TYPE, default=CONNECTION_TCP): vol.In([CONNECTION_TCP]),
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
            vol.Required("slave", default=DEFAULT_SLAVE): vol.All(vol.Coerce(int), vol.Range(min=1, max=247)),
            vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
            vol.Required("address_offset", default=0): vol.In([0, 1]),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
