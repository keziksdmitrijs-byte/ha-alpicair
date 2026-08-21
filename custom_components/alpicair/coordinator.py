"""Modbus coordinator for AlpicAir."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    COIL_INTENSIVE_AIR_FLOW, COIL_NIGHT_COOLING_FUNCTION, MODE_BUILDING_PROTECTION,
    MODE_COMFORT, MODE_ECONOMY, MODE_STANDBY, REG_AIR_FLOW_1_EXTRACT,
    REG_AIR_FLOW_1_SUPPLY, REG_AIR_FLOW_2_EXTRACT, REG_AIR_FLOW_2_SUPPLY,
    REG_AIR_FLOW_3_EXTRACT, REG_AIR_FLOW_3_SUPPLY, REG_AIR_FLOW_4_EXTRACT,
    REG_AIR_FLOW_4_SUPPLY, REG_ALARM_A, REG_ALARM_B, REG_BUILDING_PROTECTION_TEMPERATURE,
    REG_COMFORT_TEMPERATURE, REG_ECONOMY_TEMPERATURE, REG_EXHAUST_TEMPERATURE,
    REG_EXTRACT_TEMPERATURE, REG_HEAT_EXCHANGER_PRESSURE,
    REG_NIGHT_COOLING_SETPOINT, REG_NIGHT_COOLING_START_EXTRACT,
    REG_NIGHT_COOLING_START_HOURS, REG_NIGHT_COOLING_START_MINS,
    REG_NIGHT_COOLING_START_OUTDOOR, REG_NIGHT_COOLING_STOP_EXTRACT,
    REG_NIGHT_COOLING_STOP_HOURS, REG_NIGHT_COOLING_STOP_MINS, REG_OUTDOOR_TEMPERATURE,
    REG_SUPPLY_TEMPERATURE, REG_SYSTEM_MODE,
)

_LOGGER = logging.getLogger(__name__)

REGISTERS = {
    "system_mode": REG_SYSTEM_MODE,
    "comfort_temperature": REG_COMFORT_TEMPERATURE,
    "economy_temperature": REG_ECONOMY_TEMPERATURE,
    "building_protection_temperature": REG_BUILDING_PROTECTION_TEMPERATURE,
    "night_cooling_start_hours": REG_NIGHT_COOLING_START_HOURS,
    "night_cooling_start_mins": REG_NIGHT_COOLING_START_MINS,
    "night_cooling_stop_hours": REG_NIGHT_COOLING_STOP_HOURS,
    "night_cooling_stop_mins": REG_NIGHT_COOLING_STOP_MINS,
    "night_cooling_start_extract": REG_NIGHT_COOLING_START_EXTRACT,
    "night_cooling_stop_extract": REG_NIGHT_COOLING_STOP_EXTRACT,
    "night_cooling_start_outdoor": REG_NIGHT_COOLING_START_OUTDOOR,
    "night_cooling_setpoint": REG_NIGHT_COOLING_SETPOINT,
    "supply_air_flow_stage_1": REG_AIR_FLOW_1_SUPPLY,
    "supply_air_flow_stage_2": REG_AIR_FLOW_2_SUPPLY,
    "supply_air_flow_stage_3": REG_AIR_FLOW_3_SUPPLY,
    "supply_air_flow_stage_4": REG_AIR_FLOW_4_SUPPLY,
    "extract_air_flow_stage_1": REG_AIR_FLOW_1_EXTRACT,
    "extract_air_flow_stage_2": REG_AIR_FLOW_2_EXTRACT,
    "extract_air_flow_stage_3": REG_AIR_FLOW_3_EXTRACT,
    "extract_air_flow_stage_4": REG_AIR_FLOW_4_EXTRACT,
    "alarm_a": REG_ALARM_A,
    "alarm_b": REG_ALARM_B,
    "supply_temperature": REG_SUPPLY_TEMPERATURE,
    "extract_temperature": REG_EXTRACT_TEMPERATURE,
    "exhaust_temperature": REG_EXHAUST_TEMPERATURE,
    "outdoor_temperature": REG_OUTDOOR_TEMPERATURE,
    "heat_exchanger_pressure": REG_HEAT_EXCHANGER_PRESSURE,
}


class AlpicAirCoordinator(DataUpdateCoordinator[dict[str, int | bool]]):
    """Read and write registers for one controller."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.entry = entry
        self._slave = entry.data["slave"]
        self._offset = entry.data.get("address_offset", 0)
        self._client = AsyncModbusTcpClient(entry.data[CONF_HOST], port=entry.data[CONF_PORT])
        self.last_normal_mode = MODE_COMFORT
        super().__init__(
            hass,
            _LOGGER,
            name=entry.title,
            update_interval=timedelta(seconds=entry.data[CONF_SCAN_INTERVAL]),
        )

    def _address(self, documented_address: int) -> int:
        return documented_address - self._offset

    async def _connect(self) -> None:
        if not self._client.connected:
            await self._client.connect()
        if not self._client.connected:
            raise ConfigEntryNotReady("Cannot connect to the Modbus controller")

    async def _read_register(self, address: int) -> int:
        response = await self._client.read_holding_registers(
            address=self._address(address), count=1, device_id=self._slave
        )
        if response.isError():
            raise ModbusException(str(response))
        return response.registers[0]

    async def _async_update_data(self) -> dict[str, int | bool]:
        try:
            await self._connect()
            data: dict[str, int | bool] = {}
            for key, address in REGISTERS.items():
                data[key] = await self._read_register(address)
            coils = await self._client.read_coils(
                address=self._address(COIL_NIGHT_COOLING_FUNCTION), count=2, device_id=self._slave
            )
            if coils.isError():
                raise ModbusException(str(coils))
            data["night_cooling"] = coils.bits[0]
            data["intensive"] = coils.bits[1]
            if data["system_mode"] in (MODE_BUILDING_PROTECTION, MODE_ECONOMY, MODE_COMFORT):
                self.last_normal_mode = int(data["system_mode"])
            return data
        except (ModbusException, OSError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"Modbus update failed: {err}") from err

    async def async_write_register(self, documented_address: int, value: int) -> None:
        await self._connect()
        response = await self._client.write_register(
            address=self._address(documented_address), value=value, device_id=self._slave
        )
        if response.isError():
            raise HomeAssistantError(f"Modbus write failed: {response}")
        await self.async_request_refresh()

    async def async_write_coil(self, documented_address: int, value: bool) -> None:
        await self._connect()
        response = await self._client.write_coil(
            address=self._address(documented_address), value=value, device_id=self._slave
        )
        if response.isError():
            raise HomeAssistantError(f"Modbus coil write failed: {response}")
        await self.async_request_refresh()

    async def async_set_mode(self, mode: int | str) -> None:
        if mode == "intensive":
            await self.async_write_coil(COIL_INTENSIVE_AIR_FLOW, True)
            return
        await self.async_write_coil(COIL_INTENSIVE_AIR_FLOW, False)
        await self.async_write_register(REG_SYSTEM_MODE, int(mode))
        if mode in (MODE_BUILDING_PROTECTION, MODE_ECONOMY, MODE_COMFORT):
            self.last_normal_mode = int(mode)

    async def async_set_standby(self, enabled: bool) -> None:
        if enabled:
            mode = self.data.get("system_mode") if self.data else None
            if mode in (MODE_BUILDING_PROTECTION, MODE_ECONOMY, MODE_COMFORT):
                self.last_normal_mode = int(mode)
            await self.async_write_coil(COIL_INTENSIVE_AIR_FLOW, False)
            await self.async_write_register(REG_SYSTEM_MODE, MODE_STANDBY)
        else:
            await self.async_write_register(REG_SYSTEM_MODE, self.last_normal_mode)

    def active_temperature_register(self) -> int | None:
        mode = self.data.get("system_mode") if self.data else None
        if mode == MODE_BUILDING_PROTECTION:
            return REG_BUILDING_PROTECTION_TEMPERATURE
        if mode == MODE_ECONOMY:
            return REG_ECONOMY_TEMPERATURE
        if mode == MODE_COMFORT:
            return REG_COMFORT_TEMPERATURE
        if self.last_normal_mode == MODE_BUILDING_PROTECTION:
            return REG_BUILDING_PROTECTION_TEMPERATURE
        if self.last_normal_mode == MODE_ECONOMY:
            return REG_ECONOMY_TEMPERATURE
        return REG_COMFORT_TEMPERATURE

    async def async_close(self) -> None:
        self._client.close()
