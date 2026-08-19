"""Switch platform for AlpicAir boolean coils (auxiliary settings only).

Note: operating modes (Building protection / Economy / Comfort / Intensive
boost) are NOT represented as switches - they live in select.py as a single
dropdown, and Off lives in button.py as a dedicated button. Putting a
multi-valued register behind several independent switches was a known
pitfall in similar community Modbus packages (multiple switches could show
"on" simultaneously), so it is intentionally avoided here.
"""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    COIL_DRYNESS_PROTECTION,
    COIL_NIGHT_COOLING_FUNCTION,
    COIL_FULL_RECIRC_BUILDING_PROTECTION,
    COIL_FULL_RECIRC_ECONOMY,
    COIL_AIR_FLOW_CONTROL_BY_RH,
)

SWITCHES = [
    ("dryness_protection", COIL_DRYNESS_PROTECTION, "Защита от сухости", "mdi:water-percent"),
    ("night_cooling", COIL_NIGHT_COOLING_FUNCTION, "Ночное охлаждение", "mdi:weather-night"),
    ("full_recirc_building_protection", COIL_FULL_RECIRC_BUILDING_PROTECTION,
     "Рециркуляция в режиме защиты", "mdi:recycle"),
    ("full_recirc_economy", COIL_FULL_RECIRC_ECONOMY, "Рециркуляция в эконом-режиме", "mdi:recycle"),
    ("air_flow_by_rh", COIL_AIR_FLOW_CONTROL_BY_RH, "Расход воздуха по влажности", "mdi:water"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            AlpicAirCoilSwitch(coordinator, entry, key, address, name, icon)
            for key, address, name, icon in SWITCHES
        ]
    )


class AlpicAirCoilSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, entry: ConfigEntry, data_key: str, address: int, name: str, icon: str) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._data_key = data_key
        self._address = address
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_name = name
        self._attr_icon = icon

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="AlpicAir",
            model="MCB 1.27 (OEM SALDA)",
        )

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get(self._data_key))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_write_coil(self._address, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_write_coil(self._address, False)
