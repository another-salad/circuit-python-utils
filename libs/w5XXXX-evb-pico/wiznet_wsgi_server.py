""""
Circuit python - Wrappers for Wiznet WSGI library (https://github.com/Wiznet/RP2040-HAT-CircuitPython)

Requires the following circuit python libs:

    - adafruit_wiznet5k
    - adafruit_requests.mpy

"""

import adafruit_requests as requests
from adafruit_wsgi.wsgi_app import WSGIApp
import adafruit_wiznet5k.adafruit_wiznet5k_wsgiserver as server
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket


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
