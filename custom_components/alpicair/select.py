from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import *
async def async_setup_entry(hass,entry,add): add([ModeSelect(hass.data[DOMAIN][entry.entry_id],entry)])
class ModeSelect(CoordinatorEntity,SelectEntity):
 _attr_name="Режим вентиляции"; _attr_icon="mdi:fan"; _attr_options=["Защита здания","Эконом","Комфорт","Интенсивный обдув"]
 def __init__(self,c,e): super().__init__(c); self.e=e; self._attr_unique_id=f"{e.entry_id}_mode"
 @property
 def device_info(self): return DeviceInfo(identifiers={(DOMAIN,self.e.entry_id)},name=self.e.title,manufacturer="AlpicAir",model="MCB 1.27 (OEM SALDA)")
 @property
 def current_option(self):
  if self.coordinator.data.get("intensive_boost"): return "Интенсивный обдув"
  return {1:"Защита здания",2:"Эконом",3:"Комфорт"}.get(self.coordinator.data.get("system_mode"))
 async def async_select_option(self,o):
  if o=="Интенсивный обдув": await self.coordinator.write_coil(COIL_INTENSIVE_BOOST,True)
  else: await self.coordinator.write_mode({"Защита здания":1,"Эконом":2,"Комфорт":3}[o])
