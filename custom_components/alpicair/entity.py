"""Base entity for AlpicAir Modbus."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AlpicAirCoordinator


class AlpicAirEntity(CoordinatorEntity[AlpicAirCoordinator]):
    """Common entity implementation."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AlpicAirCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=coordinator.entry.title,
            manufacturer="AlpicAir",
            model="MCB Modbus controller",
        )
