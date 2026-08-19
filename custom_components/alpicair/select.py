from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import *
async def async_setup_entry(hass,entry,add):add([ModeSelect(hass.data[DOMAIN][entry.entry_id],entry)])
class ModeSelect(CoordinatorEntity,SelectEntity):
 _attr_name="Режим вентиляции";_attr_icon="mdi:fan";_attr_options=list(MODE_OPTIONS)
 def __init__(self,c,e):super().__init__(c);self.entry=e;self._attr_unique_id=f"{e.entry_id}_mode"
 @property
 def device_info(self):return DeviceInfo(identifiers={(DOMAIN,self.entry.entry_id)},name=self.entry.title,manufacturer="AlpicAir",model="MCB 1.27 (OEM SALDA)")
 @property
 def current_option(self):
  if self.coordinator.data.get("intensive_boost"):return "Интенсивный обдув"
  return MODE_NAMES.get(self.coordinator.data.get("system_mode"))
 async def async_select_option(self,option):
  value=MODE_OPTIONS[option]
  if value is None:await self.coordinator.write_coil(COIL_BOOST,True)
  else:await self.coordinator.write_register(REG_SYSTEM_MODE,value)
