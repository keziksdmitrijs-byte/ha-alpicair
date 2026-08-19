from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST,CONF_PORT
from homeassistant.core import HomeAssistant
from .const import DOMAIN,CONF_SLAVE
from .coordinator import AlpicAirCoordinator
PLATFORMS=["sensor","number","switch","button","select"]
async def async_setup_entry(hass:HomeAssistant,entry:ConfigEntry)->bool:
    d=entry.data; c=AlpicAirCoordinator(hass,d[CONF_HOST],d[CONF_PORT],d.get(CONF_SLAVE,1)); await c.async_config_entry_first_refresh(); hass.data.setdefault(DOMAIN,{})[entry.entry_id]=c; await hass.config_entries.async_forward_entry_setups(entry,PLATFORMS); return True
async def async_unload_entry(hass:HomeAssistant,entry:ConfigEntry)->bool:
    ok=await hass.config_entries.async_unload_platforms(entry,PLATFORMS)
    if ok:hass.data[DOMAIN].pop(entry.entry_id)
    return ok
