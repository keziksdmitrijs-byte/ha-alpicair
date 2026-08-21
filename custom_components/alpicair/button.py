"""Button entities for AlpicAir Modbus."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from .const import REG_ALARMS_RESET
from .entity import AlpicAirEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([AlpicAirResetErrorsButton(hass.data[entry.domain][entry.entry_id])])


class AlpicAirResetErrorsButton(AlpicAirEntity, ButtonEntity):
    _attr_name = "Сброс ошибок"
    _attr_icon = "mdi:alert-outline"

    def __init__(self, coordinator):
        super().__init__(coordinator, "reset_errors")

    async def async_press(self) -> None:
        await self.coordinator.async_write_register(REG_ALARMS_RESET, 1)
