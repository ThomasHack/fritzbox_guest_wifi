import logging

from homeassistant.helpers.entity import Entity
from custom_components.fritzbox_guest_wifi import (FB_CONNECTION)

DEPENDENCIES = ['fritzbox_guest_wifi']

UPDATE_EVENT = 'fritzbox_connection.update'

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Volvo sensors."""
    add_devices([FritzboxGuestWifiSensor(hass)])
    return True


class FritzboxGuestWifiSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._hass=hass
        self._connection=hass.data[FB_CONNECTION]
        self._state=None
        self._hass.bus.listen(UPDATE_EVENT, self.handleEvent)
        self.update()

    def handleEvent(self, call):
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Fritzbox Guest Wifi Sensor'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Fetch new state data for the sensor."""
        self._state=self._connection.fetch_current_state()
