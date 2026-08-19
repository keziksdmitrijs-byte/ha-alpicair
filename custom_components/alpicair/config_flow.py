"""Config flow."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST,CONF_PORT,CONF_NAME
from .const import DOMAIN,DEFAULT_NAME,DEFAULT_PORT,DEFAULT_SLAVE,CONF_SLAVE
class AlpicAirConfigFlow(config_entries.ConfigFlow,domain=DOMAIN):
    VERSION=1
    async def async_step_user(self,user_input=None):
        schema=vol.Schema({vol.Required(CONF_NAME,default=DEFAULT_NAME):str,vol.Required(CONF_HOST):str,vol.Required(CONF_PORT,default=DEFAULT_PORT):int,vol.Required(CONF_SLAVE,default=DEFAULT_SLAVE):int})
        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_SLAVE]}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME],data=user_input)
        return self.async_show_form(step_id="user",data_schema=schema)
