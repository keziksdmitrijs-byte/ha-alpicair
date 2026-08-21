"""Select entities for AlpicAir Modbus."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity

from .const import MODE_BUILDING_PROTECTION, MODE_COMFORT, MODE_ECONOMY, MODE_INTENSIVE, MODE_OPTIONS, MODE_STANDBY
from .entity import AlpicAirEntity

OPTIONS = [MODE_OPTIONS[MODE_STANDBY], MODE_OPTIONS[MODE_BUILDING_PROTECTION], MODE_OPTIONS[MODE_ECONOMY], MODE_OPTIONS[MODE_COMFORT], "Интенсивный обдув"]
TO_VALUE = {value: key for key, value in MODE_OPTIONS.items()} | {"Интенсивный обдув": MODE_INTENSIVE}


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([AlpicAirModeSelect(hass.data[entry.domain][entry.entry_id])])


class AlpicAirModeSelect(AlpicAirEntity, SelectEntity):
    _attr_name = "Режим"
    _attr_options = OPTIONS

    def __init__(self, coordinator):
        super().__init__(coordinator, "mode")

    @property
    def current_option(self):
        if self.coordinator.data.get("intensive"):
            return "Интенсивный обдув"
        return MODE_OPTIONS.get(self.coordinator.data.get("system_mode"), "Standby")

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_mode(TO_VALUE[option])
