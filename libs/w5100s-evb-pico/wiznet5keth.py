""""
Circuit python - Wrappers for Wiznet Ethernet library (https://github.com/Wiznet/RP2040-HAT-CircuitPython)

Requires the following circuit python libs:

    - adafruit_wiznet5k
    - adafruit_bus_device
    - adafruit_requests.mpy

"""

import board
import busio
import digitalio
import time

# Wiznet ethernet WIZNET5K, etc
from adafruit_wiznet5k.adafruit_wiznet5k import *

# Wiznet WSGI server
import adafruit_requests as requests
from adafruit_wsgi.wsgi_app import WSGIApp
import adafruit_wiznet5k.adafruit_wiznet5k_wsgiserver as server
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket


##SPI0
SPI0_SCK = board.GP18
SPI0_TX = board.GP19
SPI0_RX = board.GP16
SPI0_CSN = board.GP17

##reset
W5X00_RSTN = board.GP20


class NetworkConfig:
    """A Netork Config object"""
    def __init__(
        self,
        mac,
        ipv4_addr=None,
        subnet_mask=None,
        default_gateway=None,
        dns=None
    ):
        self.mac = mac
        self.ipv4_addr = ipv4_addr
        self.subnet_mask = subnet_mask
        self.default_gateway = default_gateway
        self.dns = dns


def config_eth(netconfig, debug=False):
    """Configures the ethernet adaptor, return initialized ethernet object

    Args:
        netconfig (NetworkConfig): An instance of the NetworkConfig class
        debug (bool): defaults False

    """
    ethernet_rst = digitalio.DigitalInOut(W5X00_RSTN)
    ethernet_rst.direction = digitalio.Direction.OUTPUT
    chip_select_pin = digitalio.DigitalInOut(SPI0_CSN)
    spi_bus = busio.SPI(SPI0_SCK, MOSI=SPI0_TX, MISO=SPI0_RX)

    # Reset W5500 first
    ethernet_rst.value = False
    time.sleep(2)  # From the example code, this apparently stops race conditions on some boards. I'm paranoid, so I'm leaving it in.
    ethernet_rst.value = True

    # we always need a mac address
    if not netconfig.mac:
        raise Exception("Must provide mac address to NetworkConfig")

    mac_addr = tuple((int(x, 16) for x in netconfig.mac.split(":")))
    if not all([netconfig.ipv4_addr, netconfig.subnet_mask, netconfig.default_gateway, netconfig.dns]):  # DHCP mode
        print("Assuming DHCP setup as some/all network config values were set to None")
        eth = WIZNET5K(spi_bus, chip_select_pin, is_dhcp=True, mac=mac_addr, debug=debug)
    else:
        print("Setting manual configuration from config.json file")
        eth = WIZNET5K(spi_bus, chip_select_pin, is_dhcp=False, mac=mac_addr, debug=debug)
        eth.ifconfig(netconfig.ipv4_addr, netconfig.subnet_mask, netconfig.default_gateway, netconfig.dns)

    print("Chip Version:", eth.chip)
    print("MAC Address:", [hex(i) for i in eth.mac_address])
    print("IP address:", eth.pretty_ip(eth.ip_address))
    # Return initialized WIZNET5K ethernet
    return eth


def wsgi_web_server(eth, listening_port=80):
    """Returns a a configured WSGI server and web app object.

    Params:
      - eth (WIZNET5K): A configured ethernet object. Returned from config_eth()
      - listening_port (int): The port for the web app to listen on
    """
    requests.set_socket(socket, eth)  # Initialize a requests object with a socket and ethernet interface
    server.set_interface(eth)
    web_app = WSGIApp()  # WSGI web app
    return (server.WSGIServer(listening_port, application=web_app), web_app)
