import logging
import voluptuous as vol
import fritzconnection as fc
import homeassistant.helpers.config_validation as cv

from datetime import timedelta
from homeassistant.const import (CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD)
from fritzconnection.fritzconnection import ServiceError, ActionError

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)

DOMAIN = 'fritzbox_guest_wifi'

REQUIREMENTS = ['fritzconnection==0.6.5']

FB_CONNECTION = 'fritzbox_connection'
UPDATE_EVENT = 'fritzbox_connection.update'

DEFAULT_HOST = 'fritz.box'
DEFAULT_PORT = 49000

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    _LOGGER.debug("starting setup")

    """Setup the sensor platform."""
    connection = FritzboxConnection(hass, config)

    hass.data[FB_CONNECTION] = connection

    hass.services.register(DOMAIN, 'turn_guestwifi_on', connection.turn_on)
    hass.services.register(DOMAIN, 'turn_guestwifi_off', connection.turn_off)

    return True


class FritzboxConnection(object):
    """Representation of the Connection."""

    def __init__(self, hass, config):
        """Initialize the connection."""
        host = config[DOMAIN].get(CONF_HOST)
        port = config[DOMAIN].get(CONF_PORT)
        username = config[DOMAIN].get(CONF_USERNAME)
        password = config[DOMAIN].get(CONF_PASSWORD)

        self._hass = hass
        self._connection = fc.FritzConnection(
            address=host,
            port=port,
            user=username,
            password=password
        )

    def turn_on(self, call):
        """Turn on guest wifi."""
        _LOGGER.info('Turning on guest wifi.')
        self._toggle(True)

    def turn_off(self, call):
        """Turn off guest wifi."""
        _LOGGER.info('Turning off guest wifi.')
        self._toggle(False)

    def reconnect(self, call):
        """Reconnect to the device."""
        _LOGGER.info('Reconnecting the fritzbox.')
        self._connection.reconnect()

    def fetch_current_state(self):
        """Fetch current state of guest wifi."""
        try:
            info = self._connection.call_action('WLANConfiguration:3', 'GetInfo')
            state = info.get("NewEnable") == "1"
            return state
        except ServiceError or ActionError:
            _LOGGER.error('Error while calling the Fritzbox Service.')

    def _toggle(self, enabled):
        """Toggle guest wifi on/off."""
        new_state = '1' if enabled else '0'

        try:
            self._connection.call_action('WLANConfiguration:3', 'SetEnable', NewEnable=new_state)
            self._hass.bus.fire(UPDATE_EVENT)
        except ServiceError or ActionError:
            _LOGGER.error('Error while calling the Fritzbox Service.')
