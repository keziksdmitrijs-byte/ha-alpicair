"""Select platform for AlpicAir: operating modes + intensive boost as a dropdown."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, COIL_INTENSIVE_AIR_FLOW_BOOST

OPTION_PROTECTION = "Защита здания"
OPTION_ECONOMY = "Эконом"
OPTION_COMFORT = "Комфорт"
OPTION_INTENSIVE = "Интенсивный обдув"

MODE_OPTIONS = [OPTION_PROTECTION, OPTION_ECONOMY, OPTION_COMFORT, OPTION_INTENSIVE]

MODE_TO_REGISTER_VALUE = {
    OPTION_PROTECTION: 1,
    OPTION_ECONOMY: 2,
    OPTION_COMFORT: 3,
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AlpicAirModeSelect(coordinator, entry)])


class AlpicAirModeSelect(CoordinatorEntity, SelectEntity):
    """Dropdown to pick Building protection / Economy / Comfort / Intensive boost.

    'Off' (Standby) is intentionally NOT included here - it is handled by a
    separate dedicated button so it stays a single, unambiguous action.
    """

    _attr_icon = "mdi:fan"
    _attr_options = MODE_OPTIONS

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_mode_select"
        self._attr_name = "Режим вентиляции"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="AlpicAir",
            model="MCB 1.27 (OEM SALDA)",
        )

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data.get("intensive_boost"):
            return OPTION_INTENSIVE
        mode = self.coordinator.data.get("system_mode")
        for option, value in MODE_TO_REGISTER_VALUE.items():
            if value == mode:
                return option
        return None

    async def async_select_option(self, option: str) -> None:
        if option == OPTION_INTENSIVE:
            await self.coordinator.async_write_coil(COIL_INTENSIVE_AIR_FLOW_BOOST, True)
            return
        value = MODE_TO_REGISTER_VALUE[option]
        await self.coordinator.async_write_system_mode(value)
