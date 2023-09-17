""""
Circuit python - Wrappers for Wiznet Ethernet library (https://github.com/Wiznet/RP2040-HAT-CircuitPython)

Requires the following circuit python libs:

    - adafruit_wiznet5k
    - adafruit_bus_device

"""

import board
import busio
import digitalio
import time

# Wiznet ethernet WIZNET5K, etc
from adafruit_wiznet5k.adafruit_wiznet5k import *

##SPI0
SPI0_SCK = board.GP18
SPI0_TX = board.GP19
SPI0_RX = board.GP16
SPI0_CSN = board.GP17

##reset
W5X00_RSTN = board.GP20

def net_str_to_tuple(input_str: str, base: int = 10, sep: str = ".") -> tuple:
    """Converts a string to a tuple of ints, returns None if input_str is None
    NOTE:
    I would use typing here, but I can't be bothered to deal with the runtime import sadness as its not important.
    Just note, input_str CAN be None, and this function will return None if it is.
    """
    if input_str:
        return tuple((int(x, base) for x in input_str.split(sep)))

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
        self.mac = net_str_to_tuple(mac, 16, ":")
        self.ipv4_addr = net_str_to_tuple(ipv4_addr)
        self.subnet_mask = net_str_to_tuple(subnet_mask)
        self.default_gateway = net_str_to_tuple(default_gateway)
        self.dns = net_str_to_tuple(dns)


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

    if not all([netconfig.ipv4_addr, netconfig.subnet_mask, netconfig.default_gateway, netconfig.dns]):  # DHCP mode
        print("Assuming DHCP setup as some/all network config values were set to None")
        eth = WIZNET5K(spi_bus, chip_select_pin, is_dhcp=True, mac=netconfig.mac, debug=debug)
    else:
        print("Setting manual configuration from config.json file")
        eth = WIZNET5K(spi_bus, chip_select_pin, is_dhcp=False, mac=netconfig.mac, debug=debug)
        eth.ifconfig = (netconfig.ipv4_addr, netconfig.subnet_mask, netconfig.default_gateway, netconfig.dns)

    print("Chip Version:", eth.chip)
    print("MAC Address:", [hex(i) for i in eth.mac_address])
    print("IP address:", eth.pretty_ip(eth.ip_address))
    # Return initialized WIZNET5K ethernet
    return eth
