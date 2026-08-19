from homeassistant.components.sensor import SensorEntity,SensorDeviceClass,SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import *
TEMPS=[("supply_temp","Температура притока"),("extract_temp","Температура вытяжки"),("exhaust_temp","Температура выброса"),("outdoor_temp","Температура наружного воздуха"),("required_supply_temp","Требуемая температура притока")]
FLOWS=[("actual_supply_1","Факт. расход приток: Защита здания"),("actual_supply_2","Факт. расход приток: Эконом"),("actual_supply_3","Факт. расход приток: Комфорт"),("actual_supply_4","Факт. расход приток: Форсаж"),("actual_extract_1","Факт. расход вытяжка: Защита здания"),("actual_extract_2","Факт. расход вытяжка: Эконом"),("actual_extract_3","Факт. расход вытяжка: Комфорт"),("actual_extract_4","Факт. расход вытяжка: Форсаж")]
async def async_setup_entry(hass,entry,add):
 c=hass.data[DOMAIN][entry.entry_id];e=[Text(c,entry,"system_state","Состояние системы",SYSTEM_STATES),Text(c,entry,"system_mode","Текущий режим",MODE_NAMES),Num(c,entry,"intensive_time_left","Осталось форсажа","s"),Num(c,entry,"alarm_count","Активные аварии",None),Num(c,entry,"filter_days_left","Дни до замены фильтров","d"),Num(c,entry,"supply_filter_pressure","Давление приточного фильтра","Pa"),Num(c,entry,"extract_filter_pressure","Давление вытяжного фильтра","Pa"),Num(c,entry,"heat_exchanger_pressure","Давление теплообменника","Pa"),Num(c,entry,"efficiency","КПД теплообменника","%")]
 e += [Temp(c,entry,*x) for x in TEMPS]+[Num(c,entry,k,n,"m³/h") for k,n in FLOWS];add(e)
class Base(CoordinatorEntity,SensorEntity):
 def __init__(self,c,e):super().__init__(c);self.entry=e
 @property
 def device_info(self):return DeviceInfo(identifiers={(DOMAIN,self.entry.entry_id)},name=self.entry.title,manufacturer="AlpicAir",model="MCB 1.27 (OEM SALDA)")
class Num(Base):
 def __init__(self,c,e,key,name,unit):super().__init__(c,e);self.key=key;self._attr_name=name;self._attr_unique_id=f"{e.entry_id}_{key}";self._attr_native_unit_of_measurement=unit;self._attr_state_class=SensorStateClass.MEASUREMENT
 @property
 def native_value(self):return self.coordinator.data.get(self.key)
class Temp(Num):
 _attr_device_class=SensorDeviceClass.TEMPERATURE;_attr_native_unit_of_measurement="°C";_attr_suggested_display_precision=1
 def __init__(self,c,e,key,name):super().__init__(c,e,key,name,"°C")
class Text(Base):
 def __init__(self,c,e,key,name,mapping):super().__init__(c,e);self.key=key;self.mapping=mapping;self._attr_name=name;self._attr_unique_id=f"{e.entry_id}_{key}"
 @property
 def native_value(self):
  v=self.coordinator.data.get(self.key);return self.mapping.get(v,"Неизвестно")
