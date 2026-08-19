from __future__ import annotations
from homeassistant.components.sensor import SensorEntity,SensorDeviceClass,SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import *
FLOW=[("measured_supply_flow_1","Факт. расход приток, ступень 1"),("measured_supply_flow_2","Факт. расход приток, ступень 2"),("measured_supply_flow_3","Факт. расход приток, ступень 3"),("measured_supply_flow_4","Факт. расход приток, ступень 4"),("measured_extract_flow_1","Факт. расход вытяжка, ступень 1"),("measured_extract_flow_2","Факт. расход вытяжка, ступень 2"),("measured_extract_flow_3","Факт. расход вытяжка, ступень 3"),("measured_extract_flow_4","Факт. расход вытяжка, ступень 4")]
async def async_setup_entry(hass,entry,add):
 c=hass.data[DOMAIN][entry.entry_id]; e=[Text(c,entry,"state","Состояние системы",SYSTEM_STATES),Text(c,entry,"nc_active","Ночное охлаждение сейчас",{True:"Активно",False:"Не активно"}),Text(c,entry,"alarm_texts","Текущие ошибки вентиляции",None),Num(c,entry,"alarms_count","Количество активных ошибок",None),Num(c,entry,"filter_days_left","Осталось дней до замены фильтров","d")]
 e += [Temp(c,entry,k,n) for k,n in [("supply_temp","Температура притока"),("extract_temp","Температура вытяжки"),("exhaust_temp","Температура выброса"),("outdoor_temp","Температура наружного воздуха"),("required_supply_temp","Требуемая температура притока")]]
 e += [Pressure(c,entry,k,n) for k,n in [("supply_filter_pressure","Давление приточного фильтра"),("extract_filter_pressure","Давление вытяжного фильтра"),("heat_exchanger_pressure","Давление теплообменника")]]
 e += [Num(c,entry,"efficiency","КПД теплообменника","%")]+[Flow(c,entry,k,n) for k,n in FLOW]; add(e)
class B(CoordinatorEntity,SensorEntity):
 def __init__(self,c,e): super().__init__(c); self.e=e
 @property
 def device_info(self): return DeviceInfo(identifiers={(DOMAIN,self.e.entry_id)},name=self.e.title,manufacturer="AlpicAir",model="MCB 1.27 (OEM SALDA)")
class Text(B):
 def __init__(self,c,e,key,name,m): super().__init__(c,e); self.key=key; self.map=m; self._attr_name=name; self._attr_unique_id=f"{e.entry_id}_{key}"; self._attr_icon="mdi:fan"
 @property
 def native_value(self):
  v=self.coordinator.data.get(self.key); return (self.map.get(v,f"Неизвестно #{v}") if self.map else (v[0] if v else "Нет активных ошибок"))
 @property
 def extra_state_attributes(self): return {"all_errors":self.coordinator.data.get("alarm_texts",[]),"alarm_codes":self.coordinator.data.get("alarm_codes",[])}
class Num(B):
 def __init__(self,c,e,key,name,unit): super().__init__(c,e); self.key=key; self._attr_name=name; self._attr_unique_id=f"{e.entry_id}_{key}"; self._attr_native_unit_of_measurement=unit; self._attr_state_class=SensorStateClass.MEASUREMENT
 @property
 def native_value(self): return self.coordinator.data.get(self.key)
class Temp(Num):
 _attr_device_class=SensorDeviceClass.TEMPERATURE; _attr_native_unit_of_measurement="°C"; _attr_suggested_display_precision=1
 def __init__(self,c,e,key,name): super().__init__(c,e,key,name,"°C")
class Pressure(Num):
 _attr_device_class=SensorDeviceClass.PRESSURE
 def __init__(self,c,e,key,name): super().__init__(c,e,key,name,"Pa")
class Flow(Num):
 def __init__(self,c,e,key,name): super().__init__(c,e,key,name,"m³/h"); self._attr_icon="mdi:fan"
