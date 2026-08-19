"""DataUpdateCoordinator for the AlpicAir integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import pymodbus
from packaging import version

from pymodbus.client import AsyncModbusTcpClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    REG_SYSTEM_MODE,
    REG_COMFORT_SETPOINT,
    REG_AIR_FLOW_1_SUPPLY,
    REG_NIGHT_COOLING_START_HOURS,
    IR_CURRENT_SYSTEM_STATE,
    IR_INTENSIVE_TIME_LEFT,
    IR_1_SUPPLY_AIR_FLOW,
    IR_1_EXTRACT_AIR_FLOW,
    IR_SUPPLY_FILTER_PRESSURE,
    COIL_DRYNESS_PROTECTION,
    DI_CRITICAL_ALARM,
    DI_NIGHT_COOLING_FUNCTION,
    ALARM_MESSAGES,
)

_LOGGER = logging.getLogger(__name__)


def _device_kwarg_name() -> str:
    """Return 'device_id' or 'slave' depending on the installed pymodbus version.

    pymodbus >= 3.10.0 renamed the `slave=` keyword argument to `device_id=`
    on all client read/write calls. Resolving this at runtime keeps the
    integration working across whatever pymodbus version is installed.
    """
    try:
        if version.parse(pymodbus.__version__) >= version.parse("3.10.0"):
            return "device_id"
    except Exception:  # noqa: BLE001
        pass
    return "slave"


class AlpicAirCoordinator(DataUpdateCoordinator):
    """Polls the AlpicAir/SALDA MCB controller over Modbus TCP."""

    def __init__(self, hass: HomeAssistant, host: str, port: int, slave: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="alpicair",
            update_interval=timedelta(seconds=15),
        )
        self._host = host
        self._port = port
        self._slave = slave
        self._client = AsyncModbusTcpClient(host=host, port=port)
        self._device_kwarg = _device_kwarg_name()

    async def _async_update_data(self) -> dict:
        if not self._client.connected:
            await self._client.connect()
        if not self._client.connected:
            raise UpdateFailed(f"Cannot connect to {self._host}:{self._port}")

        kw = {self._device_kwarg: self._slave}

        try:
            # Holding: mode/setpoint/air flow % (1-3), night cooling settings (25-32)
            holding_main = await self._client.read_holding_registers(
                address=REG_SYSTEM_MODE, count=3, **kw
            )
            holding_night_cooling = await self._client.read_holding_registers(
                address=REG_NIGHT_COOLING_START_HOURS, count=8, **kw
            )
            # Holding: 4-speed fan presets, supply (450-453) and extract (456-459)
            fan_presets_supply = await self._client.read_holding_registers(
                address=REG_AIR_FLOW_1_SUPPLY, count=4, **kw
            )
            fan_presets_extract = await self._client.read_holding_registers(
                address=REG_AIR_FLOW_1_SUPPLY + 6, count=4, **kw
            )

            # Coils: auxiliary boolean settings
            coils = await self._client.read_coils(
                address=COIL_DRYNESS_PROTECTION, count=6, **kw
            )

            # Input registers: live temperatures, filters, efficiency, alarms count (1-31)
            ir_block1 = await self._client.read_input_registers(
                address=IR_CURRENT_SYSTEM_STATE, count=31, **kw
            )
            # Input registers: measured air flow per speed step, supply (77-80)
            ir_supply_flows = await self._client.read_input_registers(
                address=IR_1_SUPPLY_AIR_FLOW, count=4, **kw
            )
            # Input registers: measured air flow per speed step, extract (83-86)
            ir_extract_flows = await self._client.read_input_registers(
                address=IR_1_EXTRACT_AIR_FLOW, count=4, **kw
            )
            # Input registers: filter pressures, HX pressure, after-HX temp, efficiency (112-125)
            ir_block2 = await self._client.read_input_registers(
                address=IR_SUPPLY_FILTER_PRESSURE, count=14, **kw
            )

            # Discrete inputs: critical alarm / warning / night cooling active summary bits
            discretes = await self._client.read_discrete_inputs(
                address=DI_CRITICAL_ALARM, count=22, **kw
            )  # covers 188..209 (critical alarm, warning, ..., night cooling active)

            # Discrete inputs: full alarm list block (address 1..72) for detailed messages
            alarm_bits = await self._client.read_discrete_inputs(
                address=1, count=72, **kw
            )
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Modbus read failed: {err}") from err

        for resp in (
            holding_main, holding_night_cooling, fan_presets_supply, fan_presets_extract,
            coils, ir_block1, ir_supply_flows, ir_extract_flows, ir_block2, discretes, alarm_bits,
        ):
            if resp.isError():
                raise UpdateFailed("Modbus device returned an error response")

        system_mode, comfort_raw, air_flow_percent = holding_main.registers
        coil_bits = coils.bits

        nc = holding_night_cooling.registers  # index 0 -> address 25
        night_cooling_start_hours = nc[0]
        night_cooling_start_mins = nc[1]
        night_cooling_stop_hours = nc[2]
        night_cooling_stop_mins = nc[3]
        night_cooling_start_extract = self._to_signed16(nc[4]) / 10.0
        night_cooling_stop_extract = self._to_signed16(nc[5]) / 10.0
        night_cooling_start_outdoor = self._to_signed16(nc[6]) / 10.0
        night_cooling_setpoint = self._to_signed16(nc[7]) / 10.0

        ir1 = ir_block1.registers  # index 0 -> address 1 (IR_CURRENT_SYSTEM_STATE)
        current_system_state = ir1[0]
        intensive_time_left = ir1[12]                                # addr 13
        required_supply_temp = self._to_signed16(ir1[16]) / 10.0     # addr 17
        supply_temp = self._to_signed16(ir1[17]) / 10.0              # addr 18
        extract_temp = self._to_signed16(ir1[18]) / 10.0             # addr 19
        exhaust_temp = self._to_signed16(ir1[19]) / 10.0             # addr 20
        outdoor_temp = self._to_signed16(ir1[20]) / 10.0             # addr 21
        active_alarms_count = ir1[27]                                # addr 28
        filters_days_left = ir1[29]                                  # addr 30

        ir2 = ir_block2.registers  # index 0 -> address 112 (IR_SUPPLY_FILTER_PRESSURE)
        supply_filter_pressure = ir2[0]     # addr 112
        extract_filter_pressure = ir2[3]    # addr 115
        heat_exchanger_pressure = ir2[6]    # addr 118
        heat_transfer_efficiency = ir2[13]  # addr 125

        active_alarm_codes = [i + 1 for i, bit in enumerate(alarm_bits.bits[:72]) if bit]
        active_alarm_texts = [
            ALARM_MESSAGES.get(code, f"Неизвестная ошибка #{code}") for code in active_alarm_codes
        ]

        # discretes: index 0 -> address 188 (critical alarm), 1 -> 189 (warning), ...
        # address 209 (night cooling active) is at offset 209-188 = 21
        night_cooling_active = bool(discretes.bits[21]) if len(discretes.bits) > 21 else False

        return {
            "system_mode": system_mode,
            "comfort_setpoint": comfort_raw / 10.0,
            "air_flow_percent": air_flow_percent,
            "intensive_time_left": intensive_time_left,
            "fan_preset_1_supply": fan_presets_supply.registers[0],
            "fan_preset_2_supply": fan_presets_supply.registers[1],
            "fan_preset_3_supply": fan_presets_supply.registers[2],
            "fan_preset_4_supply": fan_presets_supply.registers[3],
            "fan_preset_1_extract": fan_presets_extract.registers[0],
            "fan_preset_2_extract": fan_presets_extract.registers[1],
            "fan_preset_3_extract": fan_presets_extract.registers[2],
            "fan_preset_4_extract": fan_presets_extract.registers[3],
            "measured_supply_flow_1": ir_supply_flows.registers[0],
            "measured_supply_flow_2": ir_supply_flows.registers[1],
            "measured_supply_flow_3": ir_supply_flows.registers[2],
            "measured_supply_flow_4": ir_supply_flows.registers[3],
            "measured_extract_flow_1": ir_extract_flows.registers[0],
            "measured_extract_flow_2": ir_extract_flows.registers[1],
            "measured_extract_flow_3": ir_extract_flows.registers[2],
            "measured_extract_flow_4": ir_extract_flows.registers[3],
            "dryness_protection": coil_bits[0],
            "night_cooling": coil_bits[1],
            "intensive_boost": coil_bits[2],
            "full_recirc_building_protection": coil_bits[3],
            "full_recirc_economy": coil_bits[4],
            "air_flow_by_rh": coil_bits[5],
            "night_cooling_start_hours": night_cooling_start_hours,
            "night_cooling_start_mins": night_cooling_start_mins,
            "night_cooling_stop_hours": night_cooling_stop_hours,
            "night_cooling_stop_mins": night_cooling_stop_mins,
            "night_cooling_start_extract": night_cooling_start_extract,
            "night_cooling_stop_extract": night_cooling_stop_extract,
            "night_cooling_start_outdoor": night_cooling_start_outdoor,
            "night_cooling_setpoint": night_cooling_setpoint,
            "night_cooling_active": night_cooling_active,
            "current_system_state": current_system_state,
            "required_supply_temperature": required_supply_temp,
            "supply_air_temperature": supply_temp,
            "extract_air_temperature": extract_temp,
            "exhaust_air_temperature": exhaust_temp,
            "outdoor_air_temperature": outdoor_temp,
            "active_alarms_count": active_alarms_count,
            "filters_days_left": filters_days_left,
            "supply_filter_pressure": supply_filter_pressure,
            "extract_filter_pressure": extract_filter_pressure,
            "heat_exchanger_pressure": heat_exchanger_pressure,
            "heat_transfer_efficiency": heat_transfer_efficiency,
            "critical_alarm": bool(discretes.bits[0]),
            "warning": bool(discretes.bits[1]),
            "active_alarm_codes": active_alarm_codes,
            "active_alarm_texts": active_alarm_texts,
        }

    @staticmethod
    def _to_signed16(value: int) -> int:
        """Convert an unsigned 16-bit register value to signed (temperatures can be negative)."""
        return value - 65536 if value > 32767 else value

    async def async_write_system_mode(self, value: int) -> None:
        kw = {self._device_kwarg: self._slave}
        await self._client.write_register(REG_SYSTEM_MODE, value, **kw)
        await self.async_request_refresh()

    async def async_write_comfort_setpoint(self, celsius: float) -> None:
        raw = int(round(celsius * 10))
        kw = {self._device_kwarg: self._slave}
        await self._client.write_register(REG_COMFORT_SETPOINT, raw, **kw)
        await self.async_request_refresh()

    async def async_write_coil(self, address: int, state: bool) -> None:
        kw = {self._device_kwarg: self._slave}
        await self._client.write_coil(address, state, **kw)
        await self.async_request_refresh()

    async def async_write_register(self, address: int, value: int) -> None:
        kw = {self._device_kwarg: self._slave}
        await self._client.write_register(address, value, **kw)
        await self.async_request_refresh()
