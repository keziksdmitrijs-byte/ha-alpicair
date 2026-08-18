"""DataUpdateCoordinator for the AlpicAir integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from pymodbus.client import AsyncModbusTcpClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    REG_SYSTEM_MODE,
    REG_COMFORT_SETPOINT,
    REG_AIR_FLOW_PERCENT,
    REG_INTENSIVE_TIME_LEFT,
    COIL_DRYNESS_PROTECTION,
    COIL_NIGHT_COOLING_FUNCTION,
    COIL_INTENSIVE_AIR_FLOW_BOOST,
    COIL_FULL_RECIRC_BUILDING_PROTECTION,
    COIL_FULL_RECIRC_ECONOMY,
    COIL_AIR_FLOW_CONTROL_BY_RH,
)

_LOGGER = logging.getLogger(__name__)


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

    async def _async_update_data(self) -> dict:
        if not self._client.connected:
            await self._client.connect()
        if not self._client.connected:
            raise UpdateFailed(f"Cannot connect to {self._host}:{self._port}")

        try:
            holding = await self._client.read_holding_registers(
                address=REG_SYSTEM_MODE, count=3, slave=self._slave
            )
            intensive = await self._client.read_holding_registers(
                address=REG_INTENSIVE_TIME_LEFT, count=1, slave=self._slave
            )
            coils = await self._client.read_coils(
                address=COIL_DRYNESS_PROTECTION, count=6, slave=self._slave
            )
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Modbus read failed: {err}") from err

        if holding.isError() or intensive.isError() or coils.isError():
            raise UpdateFailed("Modbus device returned an error response")

        system_mode, comfort_raw, air_flow_percent = holding.registers
        intensive_time_left = intensive.registers[0]
        coil_bits = coils.bits

        return {
            "system_mode": system_mode,
            "comfort_setpoint": comfort_raw / 10.0,
            "air_flow_percent": air_flow_percent,
            "intensive_time_left": intensive_time_left,
            "dryness_protection": coil_bits[0],
            "night_cooling": coil_bits[1],
            "intensive_boost": coil_bits[2],
            "full_recirc_building_protection": coil_bits[3],
            "full_recirc_economy": coil_bits[4],
            "air_flow_by_rh": coil_bits[5],
        }

    async def async_write_system_mode(self, value: int) -> None:
        await self._client.write_register(REG_SYSTEM_MODE, value, slave=self._slave)
        await self.async_request_refresh()

    async def async_write_comfort_setpoint(self, celsius: float) -> None:
        raw = int(round(celsius * 10))
        await self._client.write_register(REG_COMFORT_SETPOINT, raw, slave=self._slave)
        await self.async_request_refresh()

    async def async_write_coil(self, address: int, state: bool) -> None:
        await self._client.write_coil(address, state, slave=self._slave)
        await self.async_request_refresh()
