"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.components.select import (
    SelectEntity,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import comfoair.model
from . import MyConfigEntry
from .const import DOMAIN
from .coordinator import ExampleCoordinator, Device
import enum
_LOGGER = logging.getLogger(__name__)



async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py
    coordinator: ExampleCoordinator = config_entry.runtime_data.coordinator

    # Enumerate all the sensors in your data value from your DataUpdateCoordinator and add an instance of your sensor class
    # to a list for each one.
    # This maybe different in your specific case, depending on how your data is structured
    entities = [
        CASelect(coordinator, device)
        for device in coordinator.data.devices
        if device.device_type == 'select'
    ]

    # Create the sensors.
    async_add_entities(entities)


class CASelect(CoordinatorEntity, SelectEntity):
    """Implementation of a sensor."""

    def __init__(self, coordinator: ExampleCoordinator, device: Device) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_id(
            self.device.device_type, self.device_id
        )
        _LOGGER.debug("Device: %s", self.device)
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        return self.coordinator.device_info()

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return ['auto', 'away', 'low', 'middle', 'high']

    @property
    def current_option(self) -> str:
        """Return the state of the entity."""
        return comfoair.model.SetFanSpeed(self.device.state).name

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return self.device.device_unique_id

    async def async_select_option(self, option: str) -> None:
        """Select option."""
        await self.coordinator.change_mode(option)

    @property
    def icon(self) -> str:
        """Return the icon."""
        speed = comfoair.model.SetFanSpeed(self.device.state)

        match speed:
            case comfoair.model.SetFanSpeed.away:
                return 'mdi:fan-chevron-down'
            case comfoair.model.SetFanSpeed.auto:
                return 'mdi:fan-auto'
            case comfoair.model.SetFanSpeed.low:
                return 'mdi:fan-speed-1'
            case comfoair.model.SetFanSpeed.middle:
                return 'mdi:fan-speed-2'
            case comfoair.model.SetFanSpeed.high:
                return 'mdi:fan-speed-3'
            case _:
                return 'mdi:fan-alert'
