"""Sensor entities for AlpicAir Modbus."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfPressure, UnitOfTemperature

from .const import MODE_OPTIONS, TEMPERATURE_SCALE
from .entity import AlpicAirEntity


@dataclass(frozen=True, kw_only=True)
class SensorDescription:
    key: str
    name: str
    unit: str | None = None
    scale: int = 1
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = SensorStateClass.MEASUREMENT


SENSORS = (
    SensorDescription(key="supply_temperature", name="Температура притока", unit=UnitOfTemperature.CELSIUS, scale=TEMPERATURE_SCALE, device_class=SensorDeviceClass.TEMPERATURE),
    SensorDescription(key="extract_temperature", name="Температура вытяжки", unit=UnitOfTemperature.CELSIUS, scale=TEMPERATURE_SCALE, device_class=SensorDeviceClass.TEMPERATURE),
    SensorDescription(key="exhaust_temperature", name="Температура выброса", unit=UnitOfTemperature.CELSIUS, scale=TEMPERATURE_SCALE, device_class=SensorDeviceClass.TEMPERATURE),
    SensorDescription(key="outdoor_temperature", name="Температура наружного воздуха", unit=UnitOfTemperature.CELSIUS, scale=TEMPERATURE_SCALE, device_class=SensorDeviceClass.TEMPERATURE),
    SensorDescription(key="heat_exchanger_pressure", name="Давление теплообменника", unit=UnitOfPressure.PA, device_class=SensorDeviceClass.PRESSURE),
    SensorDescription(key="alarm_a", name="Авария вентиляции", state_class=None),
    SensorDescription(key="alarm_b", name="Предупреждение вентиляции", state_class=None),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[entry.domain][entry.entry_id]
    entities = [AlpicAirSensor(coordinator, description) for description in SENSORS]
    entities.append(AlpicAirModeSensor(coordinator))
    entities.append(AlpicAirHeatRecoveryEfficiencySensor(coordinator))
    async_add_entities(entities)


class AlpicAirSensor(AlpicAirEntity, SensorEntity):
    def __init__(self, coordinator, description: SensorDescription):
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self.entity_description.key)
        if raw is None:
            return None
        if self.entity_description.key in ("alarm_a", "alarm_b"):
            return "Есть" if raw else "Нет"
        return raw / self.entity_description.scale


class AlpicAirModeSensor(AlpicAirEntity, SensorEntity):
    _attr_name = "Режим системы"

    def __init__(self, coordinator):
        super().__init__(coordinator, "system_mode")

    @property
    def native_value(self):
        if self.coordinator.data.get("intensive"):
            return "Интенсивный обдув"
        return MODE_OPTIONS.get(self.coordinator.data.get("system_mode"), "Неизвестно")


class AlpicAirHeatRecoveryEfficiencySensor(AlpicAirEntity, SensorEntity):
    _attr_name = "КПД теплообменника"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator):
        super().__init__(coordinator, "heat_recovery_efficiency")

    @property
    def native_value(self):
        data = self.coordinator.data
        supply = data.get("supply_temperature")
        extract = data.get("extract_temperature")
        outdoor = data.get("outdoor_temperature")
        if None in (supply, extract, outdoor) or extract == outdoor:
            return None
        result = (supply - outdoor) / (extract - outdoor) * 100
        return round(result, 1)
