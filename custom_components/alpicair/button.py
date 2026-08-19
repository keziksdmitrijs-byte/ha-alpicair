from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import *
async def async_setup_entry(hass,entry,add):add([OffButton(hass.data[DOMAIN][entry.entry_id],entry)])
class OffButton(CoordinatorEntity,ButtonEntity):
 _attr_name="Выключить (Standby)";_attr_icon="mdi:power"
 def __init__(self,c,e):super().__init__(c);self.entry=e;self._attr_unique_id=f"{e.entry_id}_off"
 @property
 def device_info(self):return DeviceInfo(identifiers={(DOMAIN,self.entry.entry_id)},name=self.entry.title,manufacturer="AlpicAir",model="MCB 1.27 (OEM SALDA)")
 async def async_press(self):await self.coordinator.write_register(REG_SYSTEM_MODE,0)
