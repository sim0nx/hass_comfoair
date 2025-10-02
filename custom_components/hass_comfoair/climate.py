import logging

import comfoair.model

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.const

from . import MyConfigEntry
from .coordinator import CACoordinator, Device

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py
    coordinator: CACoordinator = config_entry.runtime_data.coordinator

    # Enumerate all the sensors in your data value from your DataUpdateCoordinator and add an instance of your sensor class
    # to a list for each one.
    # This maybe different in your specific case, depending on how your data is structured
    entities = [
        CAClimateBypass(coordinator, device)
        for device in coordinator.data.devices
        if device.device_type == "climate"
    ]

    # Create the sensors.
    async_add_entities(entities)


class CAClimateBypass(CoordinatorEntity, ClimateEntity):
    """Climate entity for bypass."""

    _attr_has_entity_name = True
    _attr_temperature_unit = homeassistant.const.UnitOfTemperature.CELSIUS
    _attr_min_temp = 15
    _attr_max_temp = 27
    _attr_hvac_modes = [HVACMode.HEAT]

    def __init__(self, coordinator: CACoordinator, device: Device) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id

        self._attr_name = device.name
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_target_temperature_step = 1.0
        self._attr_icon = "mdi:home-thermometer-outline"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_id(
            self.device.device_type, self.device_id
        )
        _LOGGER.debug("Device: %s", self.device)
        self._attr_current_temperature = self.device.state
        self._attr_target_temperature = self.device.state
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        return self.coordinator.device_info()

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return self.device.device_unique_id

    async def async_set_temperature(self, **kwargs):
        new_temp = kwargs.get(homeassistant.const.ATTR_TEMPERATURE)
        if new_temp is None:
            return

        _LOGGER.debug("Setting comfort temperature to %s", new_temp)

        await self.coordinator.set_comfort_temperature(new_temp)

        # trigger data refresh
        await self.coordinator.async_request_refresh()
