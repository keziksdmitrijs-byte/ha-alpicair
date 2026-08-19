"""Button platform for AlpicAir: Off + go back to previous mode."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, COIL_GO_BACK_PREVIOUS_MODE


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            AlpicAirOffButton(coordinator, entry),
            AlpicAirGoBackButton(coordinator, entry),
        ]
    )


class _Base(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="AlpicAir",
            model="MCB 1.27 (OEM SALDA)",
        )


class AlpicAirOffButton(_Base):
    """The only button kept as a dedicated button: switching the unit off (Standby)."""

    _attr_icon = "mdi:power"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_mode_off"
        self._attr_name = "Выключить (Standby)"

    async def async_press(self) -> None:
        await self.coordinator.async_write_system_mode(0)


class AlpicAirGoBackButton(_Base):
    _attr_icon = "mdi:undo"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_go_back"
        self._attr_name = "Вернуться в предыдущий режим"

    async def async_press(self) -> None:
        await self.coordinator.async_write_coil(COIL_GO_BACK_PREVIOUS_MODE, True)
