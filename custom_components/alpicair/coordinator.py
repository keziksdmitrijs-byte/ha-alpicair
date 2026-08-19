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
    IR_CURRENT_SYSTEM_STATE,
    IR_INTENSIVE_TIME_LEFT,
    IR_SUPPLY_AIR_TEMPERATURE,
    IR_ACTIVE_ALARMS_COUNT,
    IR_FILTERS_TIMER_DAYS_LEFT,
    IR_SUPPLY_FILTER_PRESSURE,
    IR_HEAT_TRANSFER_EFFICIENCY,
    COIL_DRYNESS_PROTECTION,
    DI_CRITICAL_ALARM,
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
            # Holding registers: mode, comfort setpoint, air flow %, 4-speed presets
            holding = await self._client.read_holding_registers(
                address=REG_SYSTEM_MODE, count=3, **kw
            )
            fan_presets_supply = await self._client.read_holding_registers(
                address=REG_AIR_FLOW_1_SUPPLY, count=4, **kw
            )

            # Coils: auxiliary boolean settings
            coils = await self._client.read_coils(
                address=COIL_DRYNESS_PROTECTION, count=6, **kw
            )

            # Input registers: live temperatures, filters, efficiency, alarms count
            ir_block1 = await self._client.read_input_registers(
                address=IR_CURRENT_SYSTEM_STATE, count=31, **kw
            )  # covers addr 1..31 (state, mode, air flow, temps, RH, CO2, alarms count, filter days)
            ir_block2 = await self._client.read_input_registers(
                address=IR_SUPPLY_FILTER_PRESSURE, count=14, **kw
            )  # covers addr 112..125 (filter pressures, HX pressure, after-HX temp, efficiency)

            # Discrete inputs: any critical alarm / any warning summary bits
            discretes = await self._client.read_discrete_inputs(
                address=DI_CRITICAL_ALARM, count=2, **kw
            )

            # Discrete inputs: full alarm list block (address 1..72) for detailed messages
            alarm_bits = await self._client.read_discrete_inputs(
                address=1, count=72, **kw
            )
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Modbus read failed: {err}") from err

        for resp in (holding, fan_presets_supply, coils, ir_block1, ir_block2, discretes, alarm_bits):
            if resp.isError():
                raise UpdateFailed("Modbus device returned an error response")

        system_mode, comfort_raw, air_flow_percent = holding.registers
        coil_bits = coils.bits

        ir1 = ir_block1.registers  # index 0 -> address 1 (IR_CURRENT_SYSTEM_STATE)
        current_system_state = ir1[0]
        required_supply_temp = self._to_signed16(ir1[16]) / 10.0     # addr 17
        supply_temp = self._to_signed16(ir1[17]) / 10.0              # addr 18
        extract_temp = self._to_signed16(ir1[18]) / 10.0             # addr 19
        exhaust_temp = self._to_signed16(ir1[19]) / 10.0             # addr 20
        outdoor_temp = self._to_signed16(ir1[20]) / 10.0             # addr 21
        active_alarms_count = ir1[27]                                # addr 28
        filters_days_left = ir1[29]                                  # addr 30
        intensive_time_left = ir1[12]                                # addr 13

        ir2 = ir_block2.registers  # index 0 -> address 112 (IR_SUPPLY_FILTER_PRESSURE)
        supply_filter_pressure = ir2[0]     # addr 112
        extract_filter_pressure = ir2[3]    # addr 115
        heat_exchanger_pressure = ir2[6]    # addr 118
        heat_transfer_efficiency = ir2[13]  # addr 125

        active_alarm_codes = [i + 1 for i, bit in enumerate(alarm_bits.bits[:72]) if bit]
        active_alarm_texts = [
            ALARM_MESSAGES.get(code, f"Неизвестная ошибка #{code}") for code in active_alarm_codes
        ]

        return {
            "system_mode": system_mode,
            "comfort_setpoint": comfort_raw / 10.0,
            "air_flow_percent": air_flow_percent,
            "intensive_time_left": intensive_time_left,
            "fan_preset_1_supply": fan_presets_supply.registers[0],
            "fan_preset_2_supply": fan_presets_supply.registers[1],
            "fan_preset_3_supply": fan_presets_supply.registers[2],
            "fan_preset_4_supply": fan_presets_supply.registers[3],
            "dryness_protection": coil_bits[0],
            "night_cooling": coil_bits[1],
            "intensive_boost": coil_bits[2],
            "full_recirc_building_protection": coil_bits[3],
            "full_recirc_economy": coil_bits[4],
            "air_flow_by_rh": coil_bits[5],
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
