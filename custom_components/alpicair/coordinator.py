"""Coordinator for AlpicAir ventilation unit."""
from __future__ import annotations
import logging
from datetime import timedelta
import pymodbus
from packaging import version
from pymodbus.client import AsyncModbusTcpClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import *

_LOGGER=logging.getLogger(__name__)

def _device_kwarg()->str:
    try:
        return "device_id" if version.parse(pymodbus.__version__)>=version.parse("3.10.0") else "slave"
    except Exception:
        return "slave"

class AlpicAirCoordinator(DataUpdateCoordinator):
    """Read/write MCB 1.27 registers without allowing optional data to break setup."""
    def __init__(self,hass:HomeAssistant,host:str,port:int,slave:int)->None:
        super().__init__(hass,_LOGGER,name=DOMAIN,update_interval=timedelta(seconds=15))
        self._client=AsyncModbusTcpClient(host=host,port=port)
        self._slave=slave
        self._kwarg=_device_kwarg()

    @property
    def _kw(self)->dict:
        return {self._kwarg:self._slave}

    async def _optional_holding(self,address:int,count:int,default:list[int])->list[int]:
        """Read optional holding data; do not fail the integration if unsupported."""
        try:
            response=await self._client.read_holding_registers(address=address,count=count,**self._kw)
            if response.isError():
                _LOGGER.debug("Optional holding registers %s-%s unavailable: %s",address,address+count-1,response)
                return default
            return response.registers
        except Exception as err:
            _LOGGER.debug("Optional holding registers %s-%s failed: %s",address,address+count-1,err)
            return default

    async def _optional_input(self,address:int,count:int,default:list[int])->list[int]:
        """Read optional input data; do not fail the integration if unsupported."""
        try:
            response=await self._client.read_input_registers(address=address,count=count,**self._kw)
            if response.isError():
                _LOGGER.debug("Optional input registers %s-%s unavailable: %s",address,address+count-1,response)
                return default
            return response.registers
        except Exception as err:
            _LOGGER.debug("Optional input registers %s-%s failed: %s",address,address+count-1,err)
            return default

    async def _async_update_data(self)->dict:
        if not self._client.connected:
            await self._client.connect()
        if not self._client.connected:
            raise UpdateFailed("Cannot connect to Modbus TCP device")

        try:
            # These are the stable, core user registers. A failure here means no usable connection.
            core=await self._client.read_holding_registers(address=1,count=6,**self._kw)
            if core.isError():
                raise UpdateFailed(f"Modbus error reading core registers 1-6: {core}")
            coils=await self._client.read_coils(address=3,count=6,**self._kw)
            if coils.isError():
                raise UpdateFailed(f"Modbus error reading coils 3-8: {coils}")
            state=await self._client.read_input_registers(address=1,count=31,**self._kw)
            if state.isError():
                raise UpdateFailed(f"Modbus error reading input registers 1-31: {state}")
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Modbus read failed: {err}") from err

        # All new configuration/diagnostic ranges are optional. Unsupported address ranges
        # result in unavailable values for that small group, not total integration failure.
        night=await self._optional_holding(25,8,[None]*8)
        supply_config=await self._optional_holding(450,4,[None]*4)
        extract_config=await self._optional_holding(456,4,[None]*4)
        supply_flow=await self._optional_input(77,4,[None]*4)
        extract_flow=await self._optional_input(83,4,[None]*4)
        filter_data=await self._optional_input(112,14,[None]*14)

        def signed(v):
            return None if v is None else (v-65536 if v>32767 else v)
        def temp(v):
            v=signed(v)
            return None if v is None else v/10.0
        def scaled_percent(v):
            return None if v is None else v/10.0

        m=core.registers
        c=coils.bits
        s=state.registers
        return {
            "system_mode":m[0],
            "comfort_setpoint":m[1]/10.0,
            "air_flow_percent":m[2],
            "building_protection_setpoint":m[5],
            "dryness_protection":bool(c[0]),
            "night_cooling_enabled":bool(c[1]),
            "intensive_boost":bool(c[2]),
            "full_recirc_protection":bool(c[3]),
            "full_recirc_economy":bool(c[4]),
            "flow_by_rh":bool(c[5]),
            "system_state":s[0],
            "intensive_time_left":s[12],
            "required_supply_temp":temp(s[16]),
            "supply_temp":temp(s[17]),
            "extract_temp":temp(s[18]),
            "exhaust_temp":temp(s[19]),
            "outdoor_temp":temp(s[20]),
            "alarm_count":s[27],
            "filter_days_left":s[29],
            "nc_start_hour":night[0],"nc_start_min":night[1],
            "nc_stop_hour":night[2],"nc_stop_min":night[3],
            "nc_start_extract_temp":temp(night[4]),"nc_stop_extract_temp":temp(night[5]),
            "nc_stop_outdoor_temp":temp(night[6]),"nc_supply_setpoint":temp(night[7]),
            "preset_supply_1":scaled_percent(supply_config[0]),"preset_supply_2":scaled_percent(supply_config[1]),
            "preset_supply_3":scaled_percent(supply_config[2]),"preset_supply_4":scaled_percent(supply_config[3]),
            "preset_extract_1":scaled_percent(extract_config[0]),"preset_extract_2":scaled_percent(extract_config[1]),
            "preset_extract_3":scaled_percent(extract_config[2]),"preset_extract_4":scaled_percent(extract_config[3]),
            "actual_supply_1":supply_flow[0],"actual_supply_2":supply_flow[1],"actual_supply_3":supply_flow[2],"actual_supply_4":supply_flow[3],
            "actual_extract_1":extract_flow[0],"actual_extract_2":extract_flow[1],"actual_extract_3":extract_flow[2],"actual_extract_4":extract_flow[3],
            "supply_filter_pressure":filter_data[0],"extract_filter_pressure":filter_data[3],"heat_exchanger_pressure":filter_data[6],"efficiency":filter_data[13],
        }

    async def write_register(self,address:int,value:int)->None:
        result=await self._client.write_register(address,value,**self._kw)
        if result.isError():
            raise UpdateFailed(f"Modbus write error at holding register {address}: {result}")
        await self.async_request_refresh()

    async def write_coil(self,address:int,value:bool)->None:
        result=await self._client.write_coil(address,value,**self._kw)
        if result.isError():
            raise UpdateFailed(f"Modbus write error at coil {address}: {result}")
        await self.async_request_refresh()
