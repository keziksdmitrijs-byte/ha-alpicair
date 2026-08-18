"""Button platform for AlpicAir: operating modes, off, intensive boost."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    COIL_INTENSIVE_AIR_FLOW_BOOST,
    COIL_GO_BACK_PREVIOUS_MODE,
)

MODE_BUTTONS = [
    ("mode_off", 0, "Выключить (Standby)", "mdi:power"),
    ("mode_building_protection", 1, "Защита здания", "mdi:shield-home"),
    ("mode_economy", 2, "Эконом", "mdi:leaf"),
    ("mode_comfort", 3, "Комфорт", "mdi:sofa"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        AlpicAirModeButton(coordinator, entry, key, value, name, icon)
        for key, value, name, icon in MODE_BUTTONS
    ]
    entities.append(AlpicAirIntensiveBoostButton(coordinator, entry))
    entities.append(AlpicAirGoBackButton(coordinator, entry))

    async_add_entities(entities)


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


class AlpicAirModeButton(_Base):
    """One button per system mode value (register 1)."""

    def __init__(self, coordinator, entry: ConfigEntry, key: str, value: int, name: str, icon: str) -> None:
        super().__init__(coordinator, entry)
        self._value = value
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_icon = icon

    async def async_press(self) -> None:
        await self.coordinator.async_write_system_mode(self._value)


class AlpicAirIntensiveBoostButton(_Base):
    _attr_icon = "mdi:fan-plus"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_intensive_boost"
        self._attr_name = "Интенсивный обдув"

    async def async_press(self) -> None:
        await self.coordinator.async_write_coil(COIL_INTENSIVE_AIR_FLOW_BOOST, True)


class AlpicAirGoBackButton(_Base):
    _attr_icon = "mdi:undo"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_go_back"
        self._attr_name = "Вернуться в предыдущий режим"

    async def async_press(self) -> None:
        await self.coordinator.async_write_coil(COIL_GO_BACK_PREVIOUS_MODE, True)
