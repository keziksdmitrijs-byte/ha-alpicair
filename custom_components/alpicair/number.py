"""Number platform for AlpicAir: temperature slider + fan speed presets."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberDeviceClass, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MIN_TEMP,
    MAX_TEMP,
    TEMP_STEP,
    REG_AIR_FLOW_1_SUPPLY,
    REG_AIR_FLOW_2_SUPPLY,
    REG_AIR_FLOW_3_SUPPLY,
    REG_AIR_FLOW_4_SUPPLY,
    REG_AIR_FLOW_1_EXTRACT,
    REG_AIR_FLOW_2_EXTRACT,
    REG_AIR_FLOW_3_EXTRACT,
    REG_AIR_FLOW_4_EXTRACT,
)

FAN_PRESETS = [
    ("fan_preset_1_supply", REG_AIR_FLOW_1_SUPPLY, "Расход приток, ступень 1", "mdi:fan-speed-1"),
    ("fan_preset_2_supply", REG_AIR_FLOW_2_SUPPLY, "Расход приток, ступень 2", "mdi:fan-speed-2"),
    ("fan_preset_3_supply", REG_AIR_FLOW_3_SUPPLY, "Расход приток, ступень 3", "mdi:fan-speed-3"),
    ("fan_preset_4_supply", REG_AIR_FLOW_4_SUPPLY, "Расход приток, ступень 4 (Boost)", "mdi:fan-plus"),
    ("fan_preset_1_extract", REG_AIR_FLOW_1_EXTRACT, "Расход вытяжка, ступень 1", "mdi:fan-speed-1"),
    ("fan_preset_2_extract", REG_AIR_FLOW_2_EXTRACT, "Расход вытяжка, ступень 2", "mdi:fan-speed-2"),
    ("fan_preset_3_extract", REG_AIR_FLOW_3_EXTRACT, "Расход вытяжка, ступень 3", "mdi:fan-speed-3"),
    ("fan_preset_4_extract", REG_AIR_FLOW_4_EXTRACT, "Расход вытяжка, ступень 4 (Boost)", "mdi:fan-plus"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [AlpicAirComfortSetpointNumber(coordinator, entry)]
    entities += [
        AlpicAirFanPresetNumber(coordinator, entry, key, address, name, icon)
        for key, address, name, icon in FAN_PRESETS
    ]
    async_add_entities(entities)


class _Base(CoordinatorEntity, NumberEntity):
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


class AlpicAirComfortSetpointNumber(_Base):
    """Slider to change the Comfort mode target temperature."""

    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = "°C"
    _attr_native_min_value = MIN_TEMP
    _attr_native_max_value = MAX_TEMP
    _attr_native_step = TEMP_STEP
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_comfort_setpoint_number"
        self._attr_name = "Целевая температура"

    @property
    def native_value(self):
        return self.coordinator.data["comfort_setpoint"]

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_comfort_setpoint(value)


class AlpicAirFanPresetNumber(_Base):
    """Configures the % airflow for one of the 4 fixed fan speed presets.

    Registers 450-459 store the value as 0..1000 representing 0.0-100.0%
    (x0.1 scale), matching the MCB 1.27 register table convention.
    """

    _attr_native_unit_of_measurement = "%"
    _attr_native_min_value = 0.0
    _attr_native_max_value = 100.0
    _attr_native_step = 0.5
    _attr_mode = NumberMode.BOX
    _attr_entity_category = "config"

    def __init__(self, coordinator, entry: ConfigEntry, data_key: str, address: int, name: str, icon: str) -> None:
        super().__init__(coordinator, entry)
        self._data_key = data_key
        self._address = address
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_name = name
        self._attr_icon = icon

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self._data_key)
        return raw / 10.0 if raw is not None else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_register(self._address, int(round(value * 10)))
