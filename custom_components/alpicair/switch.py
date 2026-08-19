from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import *
A=[("dryness",COIL_DRYNESS,"Защита от сухости"),("night_cooling",COIL_NIGHT_COOLING,"Ночное охлаждение"),("full_recirc_protection",COIL_FULL_RECIRC_PROTECTION,"Рециркуляция в режиме защиты"),("full_recirc_economy",COIL_FULL_RECIRC_ECONOMY,"Рециркуляция в эконом-режиме"),("flow_by_rh",COIL_FLOW_BY_RH,"Расход по влажности")]
async def async_setup_entry(hass,entry,add): add([S(hass.data[DOMAIN][entry.entry_id],entry,*x) for x in A])
class S(CoordinatorEntity,SwitchEntity):
 def __init__(self,c,e,key,address,name): super().__init__(c); self.c=c; self.key=key; self.address=address; self.e=e; self._attr_name=name; self._attr_unique_id=f"{e.entry_id}_{key}"
 @property
 def device_info(self): return DeviceInfo(identifiers={(DOMAIN,self.e.entry_id)},name=self.e.title,manufacturer="AlpicAir",model="MCB 1.27 (OEM SALDA)")
 @property
 def is_on(self): return bool(self.c.data.get(self.key))
 async def async_turn_on(self,**k): await self.c.write_coil(self.address,True)
 async def async_turn_off(self,**k): await self.c.write_coil(self.address,False)
