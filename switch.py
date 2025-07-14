"""Interfaces with the Integration 101 Template api sensors."""

import logging
from typing import Any
import typing

import openhab.items

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
)
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MyConfigEntry
from .const import DOMAIN
from .coordinator import ExampleCoordinator, Device

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
    sensors = [
        ExampleSwitch(coordinator, device)
        for device in coordinator.data.devices
        if device.device_type == 'switch'
    ]

    # Create the sensors.
    async_add_entities(sensors)


class ExampleSwitch(CoordinatorEntity, SwitchEntity):
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
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        if self.device.device_class is None:
            return SwitchDeviceClass.SWITCH

        return self.device.device_class

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        return DeviceInfo(
            name=f"ExampleDevice{self.device.device_id}",
            manufacturer="ACME Manufacturer",
            model="Switch",
            sw_version="1.0",
            identifiers={
                (
                    DOMAIN,
                    f"{self.coordinator.data.controller_name}-{self.device.device_id}",
                )
            },
        )

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return self.device.device_unique_id

    @property
    def is_on(self) -> bool:
        return self.device.state == 'ON'

    # async def async_turn_on(self, **kwargs: Any) -> None:
    #     await self.hass.async_add_executor_job(typing.cast(openhab.items.SwitchItem, self.device.ohitem).on)
    #     await self.coordinator.async_request_refresh()
    #
    # async def async_turn_off(self, **kwargs: Any) -> None:
    #     await self.hass.async_add_executor_job(typing.cast(openhab.items.SwitchItem, self.device.ohitem).off)
    #     await self.coordinator.async_request_refresh()