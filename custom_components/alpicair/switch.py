from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import *
ITEMS=[("dryness_protection",COIL_DRYNESS,"Защита от сухости"),("night_cooling_enabled",COIL_NIGHT_COOLING,"Ночное охлаждение"),("full_recirc_protection",COIL_FULL_RECIRC_PROTECTION,"Рециркуляция: защита здания"),("full_recirc_economy",COIL_FULL_RECIRC_ECONOMY,"Рециркуляция: эконом"),("flow_by_rh",COIL_FLOW_BY_RH,"Расход воздуха по влажности")]
async def async_setup_entry(hass,entry,add):add([CoilSwitch(hass.data[DOMAIN][entry.entry_id],entry,*x) for x in ITEMS])
class CoilSwitch(CoordinatorEntity,SwitchEntity):
 def __init__(self,c,e,key,address,name):super().__init__(c);self.entry=e;self.key=key;self.address=address;self._attr_name=name;self._attr_unique_id=f"{e.entry_id}_{key}"
 @property
 def device_info(self):return DeviceInfo(identifiers={(DOMAIN,self.entry.entry_id)},name=self.entry.title,manufacturer="AlpicAir",model="MCB 1.27 (OEM SALDA)")
 @property
 def is_on(self):return bool(self.coordinator.data.get(self.key))
 async def async_turn_on(self,**kwargs):await self.coordinator.write_coil(self.address,True)
 async def async_turn_off(self,**kwargs):await self.coordinator.write_coil(self.address,False)
