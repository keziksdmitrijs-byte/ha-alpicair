"""Sensor platform for AlpicAir."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SYSTEM_MODES, MODE_LABELS_RU, SYSTEM_STATE_MAP

MEASURED_FLOW_SENSORS = [
    ("measured_supply_flow_1", "Расход приток, факт. ступень 1 (Защита здания)"),
    ("measured_supply_flow_2", "Расход приток, факт. ступень 2 (Эконом)"),
    ("measured_supply_flow_3", "Расход приток, факт. ступень 3 (Комфорт)"),
    ("measured_supply_flow_4", "Расход приток, факт. ступень 4 (Форсаж)"),
    ("measured_extract_flow_1", "Расход вытяжка, факт. ступень 1 (Защита здания)"),
    ("measured_extract_flow_2", "Расход вытяжка, факт. ступень 2 (Эконом)"),
    ("measured_extract_flow_3", "Расход вытяжка, факт. ступень 3 (Комфорт)"),
    ("measured_extract_flow_4", "Расход вытяжка, факт. ступень 4 (Форсаж)"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        AlpicAirModeSensor(coordinator, entry),
        AlpicAirSystemStateSensor(coordinator, entry),
        AlpicAirComfortSetpointSensor(coordinator, entry),
        AlpicAirAirFlowSensor(coordinator, entry),
        AlpicAirIntensiveTimeLeftSensor(coordinator, entry),
        AlpicAirTemperatureSensor(coordinator, entry, "supply_air_temperature", "Температура притока", "mdi:thermometer"),
        AlpicAirTemperatureSensor(coordinator, entry, "extract_air_temperature", "Температура вытяжки", "mdi:thermometer"),
        AlpicAirTemperatureSensor(coordinator, entry, "exhaust_air_temperature", "Температура выброса", "mdi:thermometer"),
        AlpicAirTemperatureSensor(coordinator, entry, "outdoor_air_temperature", "Температура наружного воздуха", "mdi:thermometer"),
        AlpicAirTemperatureSensor(coordinator, entry, "required_supply_temperature", "Требуемая температура притока", "mdi:thermometer-lines"),
        AlpicAirFiltersDaysLeftSensor(coordinator, entry),
        AlpicAirPressureSensor(coordinator, entry, "supply_filter_pressure", "Давление приточного фильтра", "mdi:air-filter"),
        AlpicAirPressureSensor(coordinator, entry, "extract_filter_pressure", "Давление вытяжного фильтра", "mdi:air-filter"),
        AlpicAirPressureSensor(coordinator, entry, "heat_exchanger_pressure", "Давление теплообменника", "mdi:gauge"),
        AlpicAirEfficiencySensor(coordinator, entry),
        AlpicAirActiveAlarmsCountSensor(coordinator, entry),
        AlpicAirActiveAlarmsTextSensor(coordinator, entry),
        AlpicAirNightCoolingActiveSensor(coordinator, entry),
    ]
    entities += [AlpicAirMeasuredFlowSensor(coordinator, entry, key, name) for key, name in MEASURED_FLOW_SENSORS]
    async_add_entities(entities)


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


class AlpicAirSystemStateSensor(_Base):
    _attr_icon = "mdi:state-machine"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_system_state"
        self._attr_name = "Детальное состояние системы"

    @property
    def native_value(self):
        raw = self.coordinator.data.get("current_system_state")
        return SYSTEM_STATE_MAP.get(raw, f"Неизвестное состояние #{raw}")


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
        return self.coordinator.data.get("intensive_time_left")


class AlpicAirTemperatureSensor(_Base):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°C"

    def __init__(self, coordinator, entry, data_key: str, name: str, icon: str) -> None:
        super().__init__(coordinator, entry)
        self._data_key = data_key
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_name = name
        self._attr_icon = icon

    @property
    def native_value(self):
        return self.coordinator.data.get(self._data_key)


class AlpicAirFiltersDaysLeftSensor(_Base):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "d"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_filters_days_left"
        self._attr_name = "Осталось дней до замены фильтров"

    @property
    def native_value(self):
        return self.coordinator.data.get("filters_days_left")


class AlpicAirPressureSensor(_Base):
    _attr_device_class = SensorDeviceClass.PRESSURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "Pa"

    def __init__(self, coordinator, entry, data_key: str, name: str, icon: str) -> None:
        super().__init__(coordinator, entry)
        self._data_key = data_key
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_name = name
        self._attr_icon = icon

    @property
    def native_value(self):
        return self.coordinator.data.get(self._data_key)


class AlpicAirEfficiencySensor(_Base):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:recycle-variant"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_heat_transfer_efficiency"
        self._attr_name = "КПД теплообменника"

    @property
    def native_value(self):
        return self.coordinator.data.get("heat_transfer_efficiency")


class AlpicAirActiveAlarmsCountSensor(_Base):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_active_alarms_count"
        self._attr_name = "Количество активных ошибок"

    @property
    def native_value(self):
        return self.coordinator.data.get("active_alarms_count")


class AlpicAirActiveAlarmsTextSensor(_Base):
    _attr_icon = "mdi:alert"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_active_alarms_text"
        self._attr_name = "Текущие ошибки вентиляции"

    @property
    def native_value(self):
        texts = self.coordinator.data.get("active_alarm_texts") or []
        return texts[0] if texts else "Нет активных ошибок"

    @property
    def extra_state_attributes(self):
        return {
            "all_alarms": self.coordinator.data.get("active_alarm_texts") or [],
            "alarm_codes": self.coordinator.data.get("active_alarm_codes") or [],
            "critical_alarm": self.coordinator.data.get("critical_alarm"),
            "warning": self.coordinator.data.get("warning"),
        }


class AlpicAirNightCoolingActiveSensor(_Base):
    _attr_icon = "mdi:weather-night"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_night_cooling_active"
        self._attr_name = "Ночное охлаждение сейчас"

    @property
    def native_value(self):
        return "Активно" if self.coordinator.data.get("night_cooling_active") else "Не активно"


class AlpicAirMeasuredFlowSensor(_Base):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "m³/h"
    _attr_icon = "mdi:air-filter"

    def __init__(self, coordinator, entry, data_key: str, name: str) -> None:
        super().__init__(coordinator, entry)
        self._data_key = data_key
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_name = name

    @property
    def native_value(self):
        return self.coordinator.data.get(self._data_key)
