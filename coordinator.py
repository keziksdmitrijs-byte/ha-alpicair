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
    REG_INTENSIVE_TIME_LEFT,
    COIL_DRYNESS_PROTECTION,
)

_LOGGER = logging.getLogger(__name__)


def _device_kwarg_name() -> str:
    """Return 'device_id' or 'slave' depending on the installed pymodbus version.

    pymodbus >= 3.10.0 renamed the `slave=` keyword argument to `device_id=`
    on all client read/write calls (see pymodbus API changes 3.10.0). Older
    releases still expect `slave=`. Resolving this at runtime keeps the
    integration working across whatever pymodbus version Home Assistant has
    installed, instead of pinning to one release.
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
            holding = await self._client.read_holding_registers(
                address=REG_SYSTEM_MODE, count=3, **kw
            )
            intensive = await self._client.read_holding_registers(
                address=REG_INTENSIVE_TIME_LEFT, count=1, **kw
            )
            coils = await self._client.read_coils(
                address=COIL_DRYNESS_PROTECTION, count=6, **kw
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
