# -*- coding: UTF-8 -*-
# barcode-reader.py
#
# Copyright (C) 2014 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of Wheel.
#
# Wheel is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Wheel is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Wheel. If not, see <http://www.gnu.org/licenses/>.

# To kick off the script, run the following from the python directory:
#   python barcode-reader.py start|stop|restart

#standard python libs
import logging
import sys
import socket
from os import listdir
from os.path import join

#third party libs
from daemon import runner
from evdev import InputDevice, ecodes, list_devices, categorize

KIOSK = 1
SOCKET_DIR = '/tmp/uzbl'

HEADERS = {
    'User-Agent': 'BarcodeReader',
}

# TODO: Test with the 2D barcode scanner and add missing chars

SCANCODES = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

# TODO: Change device name

READER_DEVICE = "RFIDeas USB Keyboard"


logger = logging.getLogger("Barcode Reader")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/wheel/barcode-reader.log")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_socket_file():
    socket_file = listdir(SOCKET_DIR)[0]
    return join(SOCKET_DIR, socket_file)


def uzblctrl(input):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(get_socket_file())
    sock.settimeout(0.5)

    sock.send(input+'\n')

    output = ''
    try:
        while True:
            buflen = 1024*1024  # 1M
            buf = sock.recv(buflen)
            output += buf
            # Don't wait to timeout if we get short output
            if len(buf) != buflen:
                break
    except socket.timeout:
        pass
    sock.close()

    if len(output) > 0 and output[-1]:
        output = output[:-1]
    return output


class App():

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = '/var/run/wheel/barcode-reader.pid'
        self.pidfile_timeout = 5

    def run(self):
        devices = map(InputDevice, list_devices())
        for device in devices:
            if device.name == READER_DEVICE:
                dev = InputDevice(device.fn)
        try:
            dev.grab()
        except:
            logger.error("Unable to grab InputDevice")
            sys.exit(1)

        logger.info("Starting the Barcode Reader daemon...")
        while True:
            rfid = ""
            for event in dev.read_loop():
                if event.type == ecodes.EV_KEY:
                    data = categorize(event)
                    if data.keystate == 1 and data.scancode != 42: # Catch only keydown, and not Enter
                        if data.scancode == 28:
                            # We have a RFID tag
                            logger.info("RFID tag read: %s" % rfid)
                            # TODO: Update URI
                            url = "https://marmix.ig.he-arc.ch/gelato/w/rfid/%s/%s/" % (KIOSK, rfid)
                            url_string = "uri " + url
                            uzblctrl(url_string)
                            rfid = ""
                        else:
                            rfid += SCANCODES[data.scancode]


app = App()

daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve = [handler.stream]
daemon_runner.do_action()

logger.info("Terminating the Barcode Reader daemon...")