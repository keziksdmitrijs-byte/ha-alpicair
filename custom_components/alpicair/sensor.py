from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.entity import DeviceInfo
from .const import *

# Списки температур и потоков (ключи и читаемые имена)
TEMPS = [
    ("supply_temp", "Температура притока"),
    ("extract_temp", "Температура вытяжки"),
    ("exhaust_temp", "Температура выброса"),
    ("outdoor_temp", "Температура на улице"),
]

FLOWS = [
    ("actual_supply_1", "Факт. расход приток: Защита здания"),
    ("actual_supply_2", "Факт. расход приток: Эконом"),
    ("actual_supply_3", "Факт. расход приток: Комфорт"),
    ("actual_supply_4", "Факт. расход приток: Форсаж"),
    ("actual_extract_1", "Факт. расход вытяжка: Защита здания"),
    ("actual_extract_2", "Факт. расход вытяжка: Эконом"),
    ("actual_extract_3", "Факт. расход вытяжка: Комфорт"),
    ("actual_extract_4", "Факт. расход вытяжка: Форсаж"),
]


async def async_setup_entry(hass, entry, add):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Существующие сенсоры, которые читают данные из coordinator.data
    entities = [
        Text(coordinator, entry, "system_state", "Состояние системы", SYSTEM_STATES),
        Text(coordinator, entry, "system_mode", "Текущий режим", MODE_NAMES),
    ]
    entities += [Temp(coordinator, entry, *x) for x in TEMPS]
    entities += [Num(coordinator, entry, k, n, "m³/h") for k, n in FLOWS]

    # Добавляем прокси‑сенсоры для каждого потока — стабильные entity_id для Lovelace
    entities += [ProxySensor(coordinator, entry, k, n) for k, n in FLOWS]

    add(entities)


class Base(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.entry.title,
            manufacturer="AlpicAir",
            model="MCB 1.27 (OEM SALDA)",
        )


class Num(Base):
    def __init__(self, coordinator, entry, key, name, unit):
        super().__init__(coordinator, entry)
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        return self.coordinator.data.get(self.key)


class Temp(Num):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = "°C"
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry, key, name):
        super().__init__(coordinator, entry, key, name, "°C")


class Text(Base):
    def __init__(self, coordinator, entry, key, name, mapping):
        super().__init__(coordinator, entry)
        self.key = key
        self.mapping = mapping
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def native_value(self):
        v = self.coordinator.data.get(self.key)
        return self.mapping.get(v, "Неизвестно")


class ProxySensor(Base):
    """Proxy sensor mirrors a user-selected entity (chosen in integration options).

    The config entry options are expected to contain mapping:
        'actual_supply_1' -> 'sensor.some_flow_sensor', etc.

    Proxy sensor has stable unique_id: "{entry_id}_proxy_{key}"
    """

    def __init__(self, coordinator, entry, key, name):
        super().__init__(coordinator, entry)
        self.key = key
        self._attr_name = f"{name} (proxy)"
        self._attr_unique_id = f"{entry.entry_id}_proxy_{key}"
        self._state = None
        self._listener_unsub = None
        self._target_entity_id = None

    @property
    def native_value(self):
        return self._state

    @property
    def native_unit_of_measurement(self):
        # По умолчанию m³/h для потоков; можно улучшить, читая единицу целевой entity
        return "m³/h"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        # Подписываемся на целевую сущность (если задана в options)
        self._update_target_listener()

    async def async_will_remove_from_hass(self):
        if self._listener_unsub:
            self._listener_unsub()
            self._listener_unsub = None

    def _on_target_state_change(self, entity_id, old_state, new_state):
        if new_state is None:
            self._state = None
        else:
            val = new_state.state
            # Пытаемся привести к числу, если возможно
            try:
                self._state = float(val)
            except Exception:
                self._state = val
        self.async_write_ha_state()

    def _update_target_listener(self):
        # Удаляем старую подписку, если была
        if self._listener_unsub:
            self._listener_unsub()
            self._listener_unsub = None

        # Берём target entity_id из опций (если не задано — оставляем пустое состояние)
        target = self.entry.options.get(self.key)
        if not target:
            self._target_entity_id = None
            self._state = None
            self.async_write_ha_state()
            return

        self._target_entity_id = target

        # Устанавливаем начальное состояние
        st = self.hass.states.get(target)
        if st:
            try:
                self._state = float(st.state)
            except Exception:
                self._state = st.state
        else:
            self._state = None

        # Подписываемся на изменение состояния целевой сущности
        self._listener_unsub = async_track_state_change(
            self.hass, target, self._on_target_state_change
        )
        self.async_write_ha_state()

    async def async_update_options(self):
        """Вызвать при изменении опций — чтобы переключить подписку на новый target."""
        self._update_target_listener()
