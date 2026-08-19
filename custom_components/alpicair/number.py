"""Writable number entities."""
from __future__ import annotations
from homeassistant.components.number import NumberEntity,NumberDeviceClass,NumberMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import *

FLOW_PRESETS=[
 ("preset_supply_1",REG_FLOW_1_SUPPLY,"Приток: Защита здания"),("preset_supply_2",REG_FLOW_2_SUPPLY,"Приток: Эконом"),("preset_supply_3",REG_FLOW_3_SUPPLY,"Приток: Комфорт"),("preset_supply_4",REG_FLOW_4_SUPPLY,"Приток: Форсаж"),
 ("preset_extract_1",REG_FLOW_1_EXTRACT,"Вытяжка: Защита здания"),("preset_extract_2",REG_FLOW_2_EXTRACT,"Вытяжка: Эконом"),("preset_extract_3",REG_FLOW_3_EXTRACT,"Вытяжка: Комфорт"),("preset_extract_4",REG_FLOW_4_EXTRACT,"Вытяжка: Форсаж"),
]
NIGHT=[
 ("nc_start_hour",REG_NC_START_HOUR,0,23,1,"Ночное охлаждение: час начала","h",1),
 ("nc_start_min",REG_NC_START_MIN,0,59,1,"Ночное охлаждение: минута начала","min",1),
 ("nc_stop_hour",REG_NC_STOP_HOUR,0,23,1,"Ночное охлаждение: час окончания","h",1),
 ("nc_stop_min",REG_NC_STOP_MIN,0,59,1,"Ночное охлаждение: минута окончания","min",1),
 ("nc_start_extract_temp",REG_NC_START_EXTRACT_TEMP,13,30,.5,"Ночное охлаждение: t вытяжки для запуска","°C",10),
 ("nc_stop_extract_temp",REG_NC_STOP_EXTRACT_TEMP,13,30,.5,"Ночное охлаждение: t вытяжки для остановки","°C",10),
 ("nc_stop_outdoor_temp",REG_NC_STOP_OUTDOOR_TEMP,0,30,.5,"Ночное охлаждение: наружная t для остановки","°C",10),
 ("nc_supply_setpoint",REG_NC_SUPPLY_SETPOINT,0,30,.5,"Ночное охлаждение: уставка притока","°C",10),
]
async def async_setup_entry(hass,entry,add):
 c=hass.data[DOMAIN][entry.entry_id]
 add([ComfortNumber(c,entry)]+[FlowNumber(c,entry,*x) for x in FLOW_PRESETS]+[NightNumber(c,entry,*x) for x in NIGHT])
class Base(CoordinatorEntity,NumberEntity):
 def __init__(self,c,e):super().__init__(c);self.entry=e
 @property
 def device_info(self):return DeviceInfo(identifiers={(DOMAIN,self.entry.entry_id)},name=self.entry.title,manufacturer="AlpicAir",model="MCB 1.27 (OEM SALDA)")
class ComfortNumber(Base):
 _attr_device_class=NumberDeviceClass.TEMPERATURE;_attr_native_unit_of_measurement="°C";_attr_native_min_value=COMFORT_MIN;_attr_native_max_value=COMFORT_MAX;_attr_native_step=.5;_attr_mode=NumberMode.SLIDER
 def __init__(self,c,e):super().__init__(c,e);self._attr_unique_id=f"{e.entry_id}_comfort_setpoint";self._attr_name="Целевая температура Comfort"
 @property
 def native_value(self):return self.coordinator.data.get("comfort_setpoint")
 async def async_set_native_value(self,v):await self.coordinator.write_register(REG_COMFORT_SETPOINT,round(v*10))
class FlowNumber(Base):
 _attr_native_unit_of_measurement="%";_attr_native_min_value=0;_attr_native_max_value=100;_attr_native_step=.5;_attr_mode=NumberMode.SLIDER;_attr_entity_category="config";_attr_icon="mdi:fan"
 def __init__(self,c,e,key,address,name):super().__init__(c,e);self.key=key;self.address=address;self._attr_unique_id=f"{e.entry_id}_{key}";self._attr_name=name
 @property
 def native_value(self):return self.coordinator.data.get(self.key)
 async def async_set_native_value(self,v):await self.coordinator.write_register(self.address,round(v*10))
class NightNumber(Base):
 _attr_mode=NumberMode.SLIDER;_attr_entity_category="config";_attr_icon="mdi:weather-night"
 def __init__(self,c,e,key,address,minimum,maximum,step,name,unit,scale):
  super().__init__(c,e);self.key=key;self.address=address;self.scale=scale;self._attr_unique_id=f"{e.entry_id}_{key}";self._attr_name=name;self._attr_native_min_value=minimum;self._attr_native_max_value=maximum;self._attr_native_step=step;self._attr_native_unit_of_measurement=unit
 @property
 def native_value(self):return self.coordinator.data.get(self.key)
 async def async_set_native_value(self,v):await self.coordinator.write_register(self.address,round(v*self.scale))
