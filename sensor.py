"""Sensor platform for AlpicAir."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SYSTEM_MODES

MODE_LABELS_RU = {
    "standby": "Выключено",
    "building_protection": "Защита здания",
    "economy": "Эконом",
    "comfort": "Комфорт",
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            AlpicAirModeSensor(coordinator, entry),
            AlpicAirComfortSetpointSensor(coordinator, entry),
            AlpicAirAirFlowSensor(coordinator, entry),
            AlpicAirIntensiveTimeLeftSensor(coordinator, entry),
        ]
    )


class _Base(CoordinatorEntity, SensorEntity):
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


class AlpicAirModeSensor(_Base):
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_system_mode"
        self._attr_name = "Режим системы"

    @property
    def native_value(self):
        raw = self.coordinator.data["system_mode"]
        key = SYSTEM_MODES.get(raw, "unknown")
        return MODE_LABELS_RU.get(key, "Неизвестно")


class AlpicAirComfortSetpointSensor(_Base):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°C"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_comfort_setpoint"
        self._attr_name = "Целевая температура (Comfort)"

    @property
    def native_value(self):
        return self.coordinator.data["comfort_setpoint"]


class AlpicAirAirFlowSensor(_Base):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:fan-speed-1"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_air_flow_percent"
        self._attr_name = "Расход воздуха"

    @property
    def native_value(self):
        return self.coordinator.data["air_flow_percent"]


class AlpicAirIntensiveTimeLeftSensor(_Base):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "s"
    _attr_icon = "mdi:timer-sand"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_intensive_time_left"
        self._attr_name = "Осталось интенсивного обдува"

    @property
    def native_value(self):
        return self.coordinator.data["intensive_time_left"]
