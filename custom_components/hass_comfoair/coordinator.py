"""Integration 101 Template integration using DataUpdateCoordinator."""

import asyncio
from dataclasses import dataclass
from datetime import timedelta
import logging
import typing

import comfoair
import comfoair.asyncio
import comfoair.model

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


@dataclass
class Device:
    """API device."""

    device_id: int
    device_unique_id: str
    device_class: str | None
    device_type: str
    name: str
    state: typing.Any
    ca_response: comfoair.CAReponse
    uom: str | None = None
    icon: str | None = None


@dataclass
class CAAPIData:
    """Class to hold api data."""

    controller_name: str
    devices: list[Device]


class CACoordinator(DataUpdateCoordinator):
    """My CA coordinator."""

    data: CAAPIData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.host = config_entry.data[CONF_HOST]
        self.port = config_entry.data[CONF_PORT]

        # set variables from options.  You need a default here incase options have not been set
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            # Using config option here but you can just use a value.
            update_interval=timedelta(seconds=self.poll_interval),
        )

        self.devices: list[Device] = []

        # Initialise your api here
        self.api_url = f"socket://{self.host}:{self.port}"
        self.api = comfoair.asyncio.ComfoAir(self.api_url)
        self.api.add_attr_event_listener(self.ca_attr_event)

        # device information
        self.di_name = "unknown"
        self.di_manufacturer = "Zehnder"
        self.di_model = "unknown"
        self.di_sw_version = "unknown"
        self.di_device_id = self.host
        self.di_controller_name = "comfoair"

    async def _async_setup(self):
        """Set up the coordinator

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        if not self.api.running:
            await self.api.connect()

        await self.api.request_firmware_version()
        await asyncio.sleep(1)
        await self.api.request_bootloader_version()
        await asyncio.sleep(1)
        await self.api.request_version()
        await asyncio.sleep(1)

        self.init_devices()

    def init_devices(self) -> None:
        self.devices.append(
            Device(
                device_id=1,
                device_unique_id="temperature_status_outside",
                device_class=SensorDeviceClass.TEMPERATURE,
                device_type="sensor",
                name="temperature_status_outside",
                ca_response=comfoair.TEMP_STATUS_OUTSIDE,
                state=None,
            )
        )
        self.devices.append(
            Device(
                device_id=2,
                device_unique_id="temperature_status_supply",
                device_class=SensorDeviceClass.TEMPERATURE,
                device_type="sensor",
                name="temperature_status_supply",
                ca_response=comfoair.TEMP_STATUS_SUPPLY,
                state=None,
            )
        )
        self.devices.append(
            Device(
                device_id=3,
                device_unique_id="temperature_status_return",
                device_class=SensorDeviceClass.TEMPERATURE,
                device_type="sensor",
                name="temperature_status_return",
                ca_response=comfoair.TEMP_STATUS_RETURN,
                state=None,
            )
        )
        self.devices.append(
            Device(
                device_id=4,
                device_unique_id="temperature_status_exhaust",
                device_class=SensorDeviceClass.TEMPERATURE,
                device_type="sensor",
                name="temperature_status_exhaust",
                ca_response=comfoair.TEMP_STATUS_EXHAUST,
                state=None,
            )
        )

        self.devices.append(
            Device(
                device_id=5,
                device_unique_id="ventilation_set_exhaust_0",
                device_class=None,
                device_type="sensor",
                name="ventilation_set_exhaust_0",
                ca_response=comfoair.VENT_SET_EXHAUST_0,
                state=None,
                uom="%",
                icon="mdi:fan-chevron-down",
            )
        )
        self.devices.append(
            Device(
                device_id=6,
                device_unique_id="ventilation_set_exhaust_1",
                device_class=None,
                device_type="sensor",
                name="ventilation_set_exhaust_1",
                ca_response=comfoair.VENT_SET_EXHAUST_1,
                state=None,
                uom="%",
                icon="mdi:fan-speed-1",
            )
        )
        self.devices.append(
            Device(
                device_id=7,
                device_unique_id="ventilation_set_exhaust_2",
                device_class=None,
                device_type="sensor",
                name="ventilation_set_exhaust_2",
                ca_response=comfoair.VENT_SET_EXHAUST_2,
                state=None,
                uom="%",
                icon="mdi:fan-speed-2",
            )
        )
        self.devices.append(
            Device(
                device_id=8,
                device_unique_id="ventilation_set_supply_0",
                device_class=None,
                device_type="sensor",
                name="ventilation_set_supply_0",
                ca_response=comfoair.VENT_SET_SUPPLY_0,
                state=None,
                uom="%",
                icon="mdi:fan-chevron-down",
            )
        )
        self.devices.append(
            Device(
                device_id=9,
                device_unique_id="ventilation_set_supply_1",
                device_class=None,
                device_type="sensor",
                name="ventilation_set_supply_1",
                ca_response=comfoair.VENT_SET_SUPPLY_1,
                state=None,
                uom="%",
                icon="mdi:fan-speed-1",
            )
        )
        self.devices.append(
            Device(
                device_id=10,
                device_unique_id="ventilation_set_supply_2",
                device_class=None,
                device_type="sensor",
                name="ventilation_set_supply_2",
                ca_response=comfoair.VENT_SET_SUPPLY_2,
                state=None,
                uom="%",
                icon="mdi:fan-speed-2",
            )
        )
        self.devices.append(
            Device(
                device_id=11,
                device_unique_id="airflow_exhaust",
                device_class=None,
                device_type="sensor",
                name="airflow_exhaust",
                ca_response=comfoair.AIRFLOW_EXHAUST,
                state=None,
                uom="%",
            )
        )
        self.devices.append(
            Device(
                device_id=12,
                device_unique_id="airflow_supply",
                device_class=None,
                device_type="sensor",
                name="airflow_supply",
                ca_response=comfoair.AIRFLOW_SUPPLY,
                state=None,
                uom="%",
            )
        )
        self.devices.append(
            Device(
                device_id=13,
                device_unique_id="fan_speed_mode",
                device_class=None,
                device_type="select",
                name="fan_speed_mode",
                ca_response=comfoair.FAN_SPEED_MODE,
                state=None,
            )
        )
        self.devices.append(
            Device(
                device_id=14,
                device_unique_id="fan_mode_supply",
                device_class=None,
                device_type="binary_sensor",
                name="fan_mode_supply",
                ca_response=comfoair.FAN_MODE_SUPPLY,
                state=None,
            )
        )
        self.devices.append(
            Device(
                device_id=15,
                device_unique_id="ventilation_set_exhaust_3",
                device_class=None,
                device_type="sensor",
                name="ventilation_set_exhaust_3",
                ca_response=comfoair.VENT_SET_EXHAUST_3,
                state=None,
                uom="%",
                icon="mdi:fan-speed-3",
            )
        )
        self.devices.append(
            Device(
                device_id=16,
                device_unique_id="ventilation_set_supply_3",
                device_class=None,
                device_type="sensor",
                name="ventilation_set_supply_3",
                ca_response=comfoair.VENT_SET_SUPPLY_3,
                state=None,
                uom="%",
                icon="mdi:fan-speed-3",
            )
        )

        self.devices.append(
            Device(
                device_id=17,
                device_unique_id="ventilation_supply_percent",
                device_class=None,
                device_type="sensor",
                name="ventilation_supply_percent",
                ca_response=comfoair.VENT_SUPPLY_PERC,
                state=None,
                uom="%",
            )
        )
        self.devices.append(
            Device(
                device_id=18,
                device_unique_id="ventilation_return_percent",
                device_class=None,
                device_type="sensor",
                name="ventilation_return_percent",
                ca_response=comfoair.VENT_RETURN_PERC,
                state=None,
                uom="%",
            )
        )
        self.devices.append(
            Device(
                device_id=19,
                device_unique_id="ventilation_supply_rpm",
                device_class=None,
                device_type="sensor",
                name="ventilation_supply_rpm",
                ca_response=comfoair.VENT_SUPPLY_RPM,
                state=None,
                uom="RPM",
                icon="mdi:speedometer",
            )
        )
        self.devices.append(
            Device(
                device_id=20,
                device_unique_id="ventilation_return_rpm",
                device_class=None,
                device_type="sensor",
                name="ventilation_return_rpm",
                ca_response=comfoair.VENT_RETURN_RPM,
                state=None,
                uom="RPM",
                icon="mdi:speedometer",
            )
        )

        self.devices.append(
            Device(
                device_id=21,
                device_unique_id="bypass_status",
                device_class=None,
                device_type="sensor",
                name="bypass_status",
                ca_response=comfoair.BYPASS_STATUS,
                state=None,
                uom="%",
            )
        )

        self.devices.append(
            Device(
                device_id=22,
                device_unique_id="temperature_comfort",
                device_class=SensorDeviceClass.TEMPERATURE,
                device_type="sensor",
                name="temperature_comfort",
                ca_response=comfoair.TEMP_COMFORT,
                state=None,
            )
        )
        self.devices.append(
            Device(
                device_id=23,
                device_unique_id="temperature_outside",
                device_class=SensorDeviceClass.TEMPERATURE,
                device_type="sensor",
                name="temperature_outside",
                ca_response=comfoair.TEMP_OUTSIDE,
                state=None,
            )
        )
        self.devices.append(
            Device(
                device_id=24,
                device_unique_id="temperature_supply",
                device_class=SensorDeviceClass.TEMPERATURE,
                device_type="sensor",
                name="temperature_supply",
                ca_response=comfoair.TEMP_SUPPLY,
                state=None,
            )
        )
        self.devices.append(
            Device(
                device_id=25,
                device_unique_id="temperature_return",
                device_class=SensorDeviceClass.TEMPERATURE,
                device_type="sensor",
                name="temperature_return",
                ca_response=comfoair.TEMP_RETURN,
                state=None,
            )
        )
        self.devices.append(
            Device(
                device_id=26,
                device_unique_id="temperature_exhaust",
                device_class=SensorDeviceClass.TEMPERATURE,
                device_type="sensor",
                name="temperature_exhaust",
                ca_response=comfoair.TEMP_EXHAUST,
                state=None,
            )
        )

        self.devices.append(
            Device(
                device_id=27,
                device_unique_id="errors_filter",
                device_class=None,
                device_type="sensor",
                name="errors_filter",
                ca_response=comfoair.ERRORS_FILTER,
                state=None,
                icon="mdi:message-alert",
            )
        )

        self.devices.append(
            Device(
                device_id=28,
                device_unique_id="running_hours_filter",
                device_class=SensorDeviceClass.DURATION,
                device_type="sensor",
                name="running_hours_filter",
                ca_response=comfoair.RUNNING_HOURS_FILTER,
                state=None,
                uom="d",
            )
        )

    async def ca_attr_event(
        self, attribute: comfoair.CAReponse, value: typing.Any
    ) -> None:
        self.logger.info("Attribute %s: %s", attribute, value)

        if attribute == comfoair.FIRMWARE_NAME:
            self.di_name = value
            self.di_model = value
            return
        if attribute == comfoair.FIRMWARE_VERSION:
            self.di_sw_version = value
            return

        for device in self.devices:
            if device.ca_response == attribute:
                device.state = value
                break

    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        return DeviceInfo(
            name=self.di_name,
            manufacturer=self.di_manufacturer,
            model=self.di_model,
            sw_version=self.di_sw_version,
            identifiers={
                (
                    DOMAIN,
                    f"{self.di_controller_name}-{self.di_device_id}",
                )
            },
        )

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            if not self.api.running:
                await self.api.connect()

            # await self.hass.async_add_executor_job(self.api.request_temperature_status)
            await self.api.request_temperature_status()
            await asyncio.sleep(2)
            await self.api.request_ventilation_status()
            await asyncio.sleep(2)
            await self.api.request_bypass_status()
            await asyncio.sleep(2)
            await self.api.request_ventilation_set()
            await asyncio.sleep(2)
            await self.api.request_temperatures()
            await asyncio.sleep(2)
            await self.api.request_errors()
            await asyncio.sleep(2)
            await self.api.request_running_hours()

        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        # What is returned here is stored in self.data by the DataUpdateCoordinator
        return CAAPIData(self.di_controller_name, self.devices)

    def get_device_by_id(self, device_type: str, device_id: int) -> Device | None:
        """Return device by device id."""
        # Called by the binary sensors and sensors to get their updated data from self.data
        try:
            return [
                device
                for device in self.data.devices
                if device.device_type == device_type and device.device_id == device_id
            ][0]
        except IndexError:
            return None

    async def change_mode(self, mode: str) -> None:
        """Change mode."""
        await self.api.set_speed(speed=comfoair.model.SetFanSpeed[mode])
