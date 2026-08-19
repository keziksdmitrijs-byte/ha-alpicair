from __future__ import annotations
from homeassistant.components.number import NumberEntity,NumberDeviceClass,NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import *
FAN_PRESETS=[("fan_preset_1_supply",REG_FLOW_1_SUPPLY,"Расход приток, ступень 1 (Защита здания)"),("fan_preset_2_supply",REG_FLOW_2_SUPPLY,"Расход приток, ступень 2 (Эконом)"),("fan_preset_3_supply",REG_FLOW_3_SUPPLY,"Расход приток, ступень 3 (Комфорт)"),("fan_preset_4_supply",REG_FLOW_4_SUPPLY,"Расход приток, ступень 4 (Форсаж)"),("fan_preset_1_extract",REG_FLOW_1_EXTRACT,"Расход вытяжка, ступень 1 (Защита здания)"),("fan_preset_2_extract",REG_FLOW_2_EXTRACT,"Расход вытяжка, ступень 2 (Эконом)"),("fan_preset_3_extract",REG_FLOW_3_EXTRACT,"Расход вытяжка, ступень 3 (Комфорт)"),("fan_preset_4_extract",REG_FLOW_4_EXTRACT,"Расход вытяжка, ступень 4 (Форсаж)")]
NC_NUMBERS=[("nc_start_hours",REG_NC_START_HOURS,0,23,1,"Ночное охлаждение: час начала","h",1),("nc_start_mins",REG_NC_START_MINS,0,59,1,"Ночное охлаждение: минута начала","min",1),("nc_stop_hours",REG_NC_STOP_HOURS,0,23,1,"Ночное охлаждение: час окончания","h",1),("nc_stop_mins",REG_NC_STOP_MINS,0,59,1,"Ночное охлаждение: минута окончания","min",1),("nc_start_extract",REG_NC_START_EXTRACT,13,30,.5,"Ночное охлаждение: температура вытяжки для запуска","°C",10),("nc_stop_extract",REG_NC_STOP_EXTRACT,13,30,.5,"Ночное охлаждение: температура вытяжки для остановки","°C",10),("nc_start_outdoor",REG_NC_START_OUTDOOR,0,30,.5,"Ночное охлаждение: наружная температура для остановки","°C",10),("nc_setpoint",REG_NC_SETPOINT,0,30,.5,"Ночное охлаждение: уставка притока","°C",10)]
async def async_setup_entry(hass,entry,async_add_entities):
 c=hass.data[DOMAIN][entry.entry_id]; e=[AlpicAirComfort(c,entry)]+[FanPreset(c,entry,*x) for x in FAN_PRESETS]+[NightCooling(c,entry,*x) for x in NC_NUMBERS]; async_add_entities(e)
class Base(CoordinatorEntity,NumberEntity):
 def __init__(self,c,e): super().__init__(c); self.e=e
 @property
 def device_info(self): return DeviceInfo(identifiers={(DOMAIN,self.e.entry_id)},name=self.e.title,manufacturer="AlpicAir",model="MCB 1.27 (OEM SALDA)")
class AlpicAirComfort(Base):
 _attr_device_class=NumberDeviceClass.TEMPERATURE; _attr_native_unit_of_measurement="°C"; _attr_native_min_value=15; _attr_native_max_value=25; _attr_native_step=.5; _attr_mode=NumberMode.SLIDER
 def __init__(self,c,e): super().__init__(c,e); self._attr_unique_id=f"{e.entry_id}_comfort"; self._attr_name="Целевая температура"
 @property
 def native_value(self): return self.coordinator.data.get("comfort_setpoint")
 async def async_set_native_value(self,v): await self.coordinator.write_comfort(v)
class FanPreset(Base):
 _attr_native_min_value=0; _attr_native_max_value=100; _attr_native_step=.5; _attr_native_unit_of_measurement="%"; _attr_mode=NumberMode.SLIDER; _attr_entity_category="config"; _attr_icon="mdi:fan"
 def __init__(self,c,e,key,address,name): super().__init__(c,e); self.key=key; self.address=address; self._attr_unique_id=f"{e.entry_id}_{key}"; self._attr_name=name
 @property
 def native_value(self): return self.coordinator.data.get(self.key,0)/10
 async def async_set_native_value(self,v): await self.coordinator.write_preset(self.address,v)
class NightCooling(Base):
 _attr_mode=NumberMode.SLIDER; _attr_entity_category="config"
 def __init__(self,c,e,key,address,mi,ma,step,name,unit,scale): super().__init__(c,e); self.key=key; self.address=address; self.scale=scale; self._attr_unique_id=f"{e.entry_id}_{key}"; self._attr_name=name; self._attr_native_min_value=mi; self._attr_native_max_value=ma; self._attr_native_step=step; self._attr_native_unit_of_measurement=unit; self._attr_icon="mdi:weather-night"
 @property
 def native_value(self): return self.coordinator.data.get(self.key)
 async def async_set_native_value(self,v): await self.coordinator.write_nc(self.address,v,self.scale)
