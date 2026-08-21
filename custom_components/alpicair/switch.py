"""Switch entities for AlpicAir Modbus."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from .const import MODE_STANDBY
from .entity import AlpicAirEntity
from .const import COIL_NIGHT_COOLING_FUNCTION


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[entry.domain][entry.entry_id]
    async_add_entities([AlpicAirNightCoolingSwitch(coordinator), AlpicAirStandbySwitch(coordinator)])


class AlpicAirNightCoolingSwitch(AlpicAirEntity, SwitchEntity):
    _attr_name = "Ночное охлаждение"

    def __init__(self, coordinator):
        super().__init__(coordinator, "night_cooling")

    @property
    def is_on(self):
        return bool(self.coordinator.data.get("night_cooling"))

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_write_coil(COIL_NIGHT_COOLING_FUNCTION, True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_write_coil(COIL_NIGHT_COOLING_FUNCTION, False)


class AlpicAirStandbySwitch(AlpicAirEntity, SwitchEntity):
    _attr_name = "Выключатель (Standby)"

    def __init__(self, coordinator):
        super().__init__(coordinator, "standby")

    @property
    def is_on(self):
        return self.coordinator.data.get("system_mode") == MODE_STANDBY

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_set_standby(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_set_standby(False)
