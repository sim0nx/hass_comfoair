"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

from dataclasses import dataclass
from enum import StrEnum
import logging
from random import choice, randrange
import openhab
import openhab.items
import re
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

_LOGGER = logging.getLogger(__name__)

# alarm status + turn off
regex_alarm = re.compile(r'''^alarm_partition_(\w+)_alarm$''')
# armed state + on/off
regex_arm_state = re.compile(r'''^alarm_partition_(\w+)$''')
# fire alarm state + turn off
regex_fire_alarm = re.compile(r'''^alarm_partition_fire_detectors_alarm$''')
# fire alarm status
regex_fire_state = re.compile(r'''^alarm_fire_(\w+)$''')
# motion sensor
regex_motion_sensor = re.compile(r'''^alarm_motion_(\w+)$''')
# reed/contact sensor
regex_reed_sensor = re.compile(r'''^alarm_reed_(\w+)$''')


class DeviceType(StrEnum):
    """Device types."""

    TEMP_SENSOR = "temp_sensor"
    DOOR_SENSOR = "door_sensor"
    SWITCH = "switch"
    BINARY_SENSOR = "binary_sensor"
    OTHER = "other"

regex_map = {
    regex_alarm: DeviceType.SWITCH,
    regex_arm_state: DeviceType.SWITCH,
    regex_fire_alarm: DeviceType.SWITCH,
    regex_fire_state: DeviceType.BINARY_SENSOR,
    regex_motion_sensor: DeviceType.BINARY_SENSOR,
    regex_reed_sensor: DeviceType.BINARY_SENSOR,
}

def oh_name_to_hass(ohitem: openhab.items.Item) -> tuple[DeviceType | None, BinarySensorDeviceClass | None]:
    for k, matched_device_type in regex_map.items():
        if k.match(ohitem.name):
            if matched_device_type == DeviceType.BINARY_SENSOR:
                if 'OpenState' in ohitem.tags and 'reed' in ohitem.name:
                    # reed contacts
                    if 'garage' in ohitem.name:
                        return matched_device_type, BinarySensorDeviceClass.GARAGE_DOOR
                    if 'keller_dir_ext' in ohitem.name:
                        return matched_device_type, BinarySensorDeviceClass.DOOR
                    if 'rdc_hall_entree_dir' in ohitem.name:
                        return matched_device_type, BinarySensorDeviceClass.DOOR

                    return matched_device_type, BinarySensorDeviceClass.WINDOW

                if 'SmokeDetector' in ohitem.tags:
                    return matched_device_type, BinarySensorDeviceClass.SMOKE

                if 'MotionDetector' in ohitem.tags:
                    return matched_device_type, BinarySensorDeviceClass.MOTION

                return matched_device_type, None

            if matched_device_type == DeviceType.SWITCH:
                return matched_device_type, None

    return None, None

@dataclass
class Device:
    """API device."""

    device_id: int
    device_unique_id: str
    device_type: DeviceType
    device_class: str | None
    name: str
    ohitem: openhab.items.Item


class API:
    """Class for example API."""

    def __init__(self, host: str, user: str, pwd: str) -> None:
        """Initialise."""
        self.host = host
        self.user = user
        self.pwd = pwd
        self.connected: bool = False

        self.api_url = 'https://haus.ten.lu/rest'
        self.api_user = 'sim0n'
        self.api_pass = 'pisargg'

        self.ohapi: openhab.OpenHAB | None = None
        self.myitems: list[openhab.items.Item] = []

    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.host.replace(".", "_")

    def connect(self) -> bool:
        """Connect to api."""
        if self.ohapi is None:
            self.ohapi = openhab.OpenHAB(self.api_url, username=self.api_user, password=self.api_pass)

        ohitems = self.ohapi.fetch_all_items()

        for iname, item in ohitems.items():
            if item.TYPENAME == 'Group' or item.group:
                continue

            if iname.startswith('alarm'):
                self.myitems.append(item)

        self.connected = True
        return True

        # raise APIAuthError("Error connecting to api. Invalid username or password.")

    def disconnect(self) -> bool:
        """Disconnect from api."""
        self.connected = False
        return True

    def get_devices(self) -> list[Device]:
        """Get devices on api."""
        devices = []

        for i, item in enumerate(self.myitems):
            d_type, d_class = oh_name_to_hass(item)

            if d_type is None:
                _LOGGER.warning('Unable to map OpenHab item: %s', item.name)
                continue

            d = Device(
                device_id=i,
                device_unique_id=self.get_device_unique_id(
                    item.name, d_type
                ),
                device_type=d_type,
                device_class=d_class,
                name=item.name,
                ohitem=item,
            )


            devices.append(d)

        return devices

        return [
            Device(
                device_id=device.get("id"),
                device_unique_id=self.get_device_unique_id(
                    device.get("id"), device.get("type")
                ),
                device_type=device.get("type"),
                name=self.get_device_name(device.get("id"), device.get("type")),
                state=self.get_device_value(device.get("id"), device.get("type")),
            )
            for device in DEVICES
        ]

    def get_device_unique_id(self, device_id: str, device_type: DeviceType) -> str:
        """Return a unique device id."""
        if device_type == DeviceType.DOOR_SENSOR:
            return f"{self.controller_name}_D{device_id}"
        if device_type == DeviceType.TEMP_SENSOR:
            return f"{self.controller_name}_T{device_id}"
        return f"{self.controller_name}_Z{device_id}"

    def get_device_name(self, device_id: str, device_type: DeviceType) -> str:
        """Return the device name."""
        if device_type == DeviceType.DOOR_SENSOR:
            return f"DoorSensor{device_id}"
        if device_type == DeviceType.TEMP_SENSOR:
            return f"TempSensor{device_id}"
        return f"OtherSensor{device_id}"

    def get_device_value(self, device_id: str, device_type: DeviceType) -> int | bool:
        """Get device random value."""
        if device_type == DeviceType.DOOR_SENSOR:
            return choice([True, False])
        if device_type == DeviceType.TEMP_SENSOR:
            return randrange(15, 28)
        return randrange(1, 10)


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""
