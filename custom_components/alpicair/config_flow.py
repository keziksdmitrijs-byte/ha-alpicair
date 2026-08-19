"""Config flow and options flow for AlpicAir."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.helpers import selector

from .const import DOMAIN, DEFAULT_NAME, DEFAULT_PORT, DEFAULT_SLAVE, CONF_SLAVE

# --- existing config flow with typo fixed ---
class AlpicAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): int,
            }
        )
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_SLAVE]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
        return self.async_show_form(step_id="user", data_schema=schema)


# --- options flow: allows user to select entity_id for each image position ---
class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        options = dict(self.config_entry.options or {})

        # Keys should match the ones used by sensor proxy creation
        flow_keys = [
            "actual_supply_1",
            "actual_supply_2",
            "actual_supply_3",
            "actual_supply_4",
            "actual_extract_1",
            "actual_extract_2",
            "actual_extract_3",
            "actual_extract_4",
        ]

        if user_input is not None:
            # Save all fields at once
            return self.async_create_entry(title="", data=user_input)

        # Build schema with entity selectors for each flow position (only sensors)
        schema_dict = {}
        for key in flow_keys:
            schema_dict[vol.Optional(key, default=options.get(key, ""))] = selector.selector(
                {"entity": {"domain": "sensor"}}
            )

        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema_dict))


async def async_get_options_flow(config_entry):
    return OptionsFlowHandler(config_entry)
