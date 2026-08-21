"""Number entities for AlpicAir Modbus."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, UnitOfTemperature

from .const import TEMPERATURE_SCALE, PERCENT_SCALE
from .entity import AlpicAirEntity


@dataclass(frozen=True, kw_only=True)
class NumberDescription:
    key: str
    name: str
    register: int | None
    minimum: float
    maximum: float
    step: float
    scale: int = 1
    unit: str | None = None
    device_class: NumberDeviceClass | None = None


NUMBERS = (
    NumberDescription(key="target_temperature", name="Целевая температура", register=None, minimum=16, maximum=30, step=0.1, scale=TEMPERATURE_SCALE, unit=UnitOfTemperature.CELSIUS, device_class=NumberDeviceClass.TEMPERATURE),
    NumberDescription(key="supply_air_flow_stage_1", name="Расход притока, ступень 1", register=450, minimum=0, maximum=100, step=0.1, scale=PERCENT_SCALE, unit=PERCENTAGE),
    NumberDescription(key="supply_air_flow_stage_2", name="Расход притока, ступень 2", register=451, minimum=0, maximum=100, step=0.1, scale=PERCENT_SCALE, unit=PERCENTAGE),
    NumberDescription(key="supply_air_flow_stage_3", name="Расход притока, ступень 3", register=452, minimum=0, maximum=100, step=0.1, scale=PERCENT_SCALE, unit=PERCENTAGE),
    NumberDescription(key="supply_air_flow_stage_4", name="Расход притока, ступень 4", register=453, minimum=0, maximum=100, step=0.1, scale=PERCENT_SCALE, unit=PERCENTAGE),
    NumberDescription(key="extract_air_flow_stage_1", name="Расход вытяжки, ступень 1", register=456, minimum=0, maximum=100, step=0.1, scale=PERCENT_SCALE, unit=PERCENTAGE),
    NumberDescription(key="extract_air_flow_stage_2", name="Расход вытяжки, ступень 2", register=457, minimum=0, maximum=100, step=0.1, scale=PERCENT_SCALE, unit=PERCENTAGE),
    NumberDescription(key="extract_air_flow_stage_3", name="Расход вытяжки, ступень 3", register=458, minimum=0, maximum=100, step=0.1, scale=PERCENT_SCALE, unit=PERCENTAGE),
    NumberDescription(key="extract_air_flow_stage_4", name="Расход вытяжки, ступень 4", register=459, minimum=0, maximum=100, step=0.1, scale=PERCENT_SCALE, unit=PERCENTAGE),
    NumberDescription(key="night_cooling_start_hours", name="Ночное охлаждение: начало, часы", register=25, minimum=0, maximum=23, step=1),
    NumberDescription(key="night_cooling_start_mins", name="Ночное охлаждение: начало, минуты", register=26, minimum=0, maximum=59, step=1),
    NumberDescription(key="night_cooling_stop_hours", name="Ночное охлаждение: окончание, часы", register=27, minimum=0, maximum=23, step=1),
    NumberDescription(key="night_cooling_stop_mins", name="Ночное охлаждение: окончание, минуты", register=28, minimum=0, maximum=59, step=1),
    NumberDescription(key="night_cooling_start_extract", name="Ночное охлаждение: температура вытяжки для запуска", register=29, minimum=13, maximum=30, step=0.1, scale=TEMPERATURE_SCALE, unit=UnitOfTemperature.CELSIUS, device_class=NumberDeviceClass.TEMPERATURE),
    NumberDescription(key="night_cooling_stop_extract", name="Ночное охлаждение: температура вытяжки для остановки", register=30, minimum=13, maximum=30, step=0.1, scale=TEMPERATURE_SCALE, unit=UnitOfTemperature.CELSIUS, device_class=NumberDeviceClass.TEMPERATURE),
    NumberDescription(key="night_cooling_start_outdoor", name="Ночное охлаждение: наружная температура", register=31, minimum=0, maximum=30, step=0.1, scale=TEMPERATURE_SCALE, unit=UnitOfTemperature.CELSIUS, device_class=NumberDeviceClass.TEMPERATURE),
    NumberDescription(key="night_cooling_setpoint", name="Ночное охлаждение: целевая температура притока", register=32, minimum=0, maximum=30, step=0.1, scale=TEMPERATURE_SCALE, unit=UnitOfTemperature.CELSIUS, device_class=NumberDeviceClass.TEMPERATURE),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[entry.domain][entry.entry_id]
    async_add_entities(AlpicAirNumber(coordinator, description) for description in NUMBERS)


class AlpicAirNumber(AlpicAirEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, description: NumberDescription):
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_native_min_value = description.minimum
        self._attr_native_max_value = description.maximum
        self._attr_native_step = description.step
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class

    @property
    def native_value(self):
        key = self.entity_description.key
        if key == "target_temperature":
            address = self.coordinator.active_temperature_register()
            lookup = {2: "comfort_temperature", 4: "economy_temperature", 6: "building_protection_temperature"}
            raw = self.coordinator.data.get(lookup[address])
        else:
            raw = self.coordinator.data.get(key)
        return None if raw is None else raw / self.entity_description.scale

    async def async_set_native_value(self, value: float) -> None:
        register = self.entity_description.register
        if register is None:
            register = self.coordinator.active_temperature_register()
        await self.coordinator.async_write_register(register, round(value * self.entity_description.scale))
