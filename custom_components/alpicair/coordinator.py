"""Modbus coordinator for AlpicAir ventilation unit."""
from __future__ import annotations
import logging
from datetime import timedelta
import pymodbus
from packaging import version
from pymodbus.client import AsyncModbusTcpClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator,UpdateFailed
from .const import *
_LOGGER=logging.getLogger(__name__)

def _device_kwarg():
    try:
        return "device_id" if version.parse(pymodbus.__version__)>=version.parse("3.10.0") else "slave"
    except Exception: return "slave"

class AlpicAirCoordinator(DataUpdateCoordinator):
    def __init__(self,hass:HomeAssistant,host:str,port:int,slave:int):
        super().__init__(hass,_LOGGER,name=DOMAIN,update_interval=timedelta(seconds=15))
        self._slave=slave; self._client=AsyncModbusTcpClient(host=host,port=port); self._kw=_device_kwarg()
    async def _async_update_data(self):
        if not self._client.connected: await self._client.connect()
        if not self._client.connected: raise UpdateFailed("Не удалось подключиться к Modbus TCP")
        kw={self._kw:self._slave}
        try:
            main=await self._client.read_holding_registers(address=1,count=6,**kw)
            nc=await self._client.read_holding_registers(address=25,count=8,**kw)
            supply_cfg=await self._client.read_holding_registers(address=450,count=4,**kw)
            extract_cfg=await self._client.read_holding_registers(address=456,count=4,**kw)
            coils=await self._client.read_coils(address=3,count=6,**kw)
            ir1=await self._client.read_input_registers(address=1,count=31,**kw)
            ir_sf=await self._client.read_input_registers(address=77,count=4,**kw)
            ir_ef=await self._client.read_input_registers(address=83,count=4,**kw)
            ir2=await self._client.read_input_registers(address=112,count=14,**kw)
            critical=await self._client.read_discrete_inputs(address=188,count=2,**kw)
            nc_active=await self._client.read_discrete_inputs(address=209,count=1,**kw)
            alarms=await self._client.read_discrete_inputs(address=1,count=72,**kw)
        except Exception as err: raise UpdateFailed(f"Modbus read failed: {err}") from err
        responses=(main,nc,supply_cfg,extract_cfg,coils,ir1,ir_sf,ir_ef,ir2,critical,nc_active,alarms)
        if any(r.isError() for r in responses): raise UpdateFailed("Modbus device returned an error response")
        m=main.registers; n=nc.registers; c=coils.bits; r=ir1.registers; p=ir2.registers
        signed=lambda x:x-65536 if x>32767 else x
        codes=[i+1 for i,b in enumerate(alarms.bits[:72]) if b]
        return {
            "system_mode":m[0],"comfort_setpoint":m[1]/10,"air_flow_percent":m[2],
            "intensive_time_left":r[12],"fan_preset_1_supply":supply_cfg.registers[0],"fan_preset_2_supply":supply_cfg.registers[1],"fan_preset_3_supply":supply_cfg.registers[2],"fan_preset_4_supply":supply_cfg.registers[3],
            "fan_preset_1_extract":extract_cfg.registers[0],"fan_preset_2_extract":extract_cfg.registers[1],"fan_preset_3_extract":extract_cfg.registers[2],"fan_preset_4_extract":extract_cfg.registers[3],
            "measured_supply_flow_1":ir_sf.registers[0],"measured_supply_flow_2":ir_sf.registers[1],"measured_supply_flow_3":ir_sf.registers[2],"measured_supply_flow_4":ir_sf.registers[3],
            "measured_extract_flow_1":ir_ef.registers[0],"measured_extract_flow_2":ir_ef.registers[1],"measured_extract_flow_3":ir_ef.registers[2],"measured_extract_flow_4":ir_ef.registers[3],
            "dryness":c[0],"night_cooling":c[1],"intensive_boost":c[2],"full_recirc_protection":c[3],"full_recirc_economy":c[4],"flow_by_rh":c[5],
            "nc_start_hours":n[0],"nc_start_mins":n[1],"nc_stop_hours":n[2],"nc_stop_mins":n[3],"nc_start_extract":signed(n[4])/10,"nc_stop_extract":signed(n[5])/10,"nc_start_outdoor":signed(n[6])/10,"nc_setpoint":signed(n[7])/10,"nc_active":bool(nc_active.bits[0]),
            "state":r[0],"supply_temp":signed(r[17])/10,"extract_temp":signed(r[18])/10,"exhaust_temp":signed(r[19])/10,"outdoor_temp":signed(r[20])/10,"required_supply_temp":signed(r[16])/10,
            "alarms_count":r[27],"filter_days_left":r[29],"supply_filter_pressure":p[0],"extract_filter_pressure":p[3],"heat_exchanger_pressure":p[6],"efficiency":p[13],"critical_alarm":bool(critical.bits[0]),"warning":bool(critical.bits[1]),"alarm_codes":codes,"alarm_texts":[ALARM_MESSAGES.get(x,f"Неизвестная ошибка #{x}") for x in codes],
        }
    async def _write(self,address,value):
        await self._client.write_register(address,value,**{self._kw:self._slave}); await self.async_request_refresh()
    async def write_coil(self,address,value):
        await self._client.write_coil(address,value,**{self._kw:self._slave}); await self.async_request_refresh()
    async def write_mode(self,value): await self._write(REG_SYSTEM_MODE,value)
    async def write_comfort(self,value): await self._write(REG_COMFORT_SETPOINT,round(value*10))
    async def write_preset(self,address,value): await self._write(address,round(value*10))
    async def write_nc(self,address,value,scale=1): await self._write(address,round(value*scale))
