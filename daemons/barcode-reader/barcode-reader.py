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
import time
import string
from subprocess import call

#third party libs
from daemon import runner
from evdev import InputDevice, ecodes, list_devices, categorize


SOCKET_DIR = '/var/socket/uzbl'

HEADERS = {
    'User-Agent': 'BarcodeReader',
}

SCANCODES = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r',
    20: u't', 21: u'z', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'y', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n',
    50: u'm', 51: u',', 52: u'.', 53: u'-', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

CAPSCODES = {
    0: None, 1: u'ESC', 2: u'!', 3: u'@', 4: u'#', 5: u'$', 6: u'%', 7: u'^', 8: u'/', 9: u'*',
    10: u'(', 11: u')', 12: u'_', 13: u'+', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Z', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'{', 27: u'}', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u':',
    40: u'\'', 41: u'~', 42: u'LSHFT', 43: u'|', 44: u'Y', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u'<', 52: u':', 53: u'?', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

ADMINCODES = {
    104: 'refresh', 105: 'shutdown'
}


READER_DEVICE = "Datalogic Scanning, Inc. Handheld Barcode Scanner"
#READER_DEVICE = "Metrologic Metrologic Scanner"

logger = logging.getLogger("Barcode Reader")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/wheel/barcode-reader.log")
handler.setFormatter(formatter)
logger.addHandler(handler)


def chromix(url):
    response = call("chromix with current goto %s" % url, shell=True)
    if response == 0:
        return True
    return False


def validate_code(code):
    # The code is in the form '32X242C3'
    code = code.lower()
    checksum = 0
    for char in code[:-1]:
        if char.isdigit():
            checksum += int(char)
        else:
            checksum += int(string.lowercase.index(char))
    if checksum % 10 == int(code[-1]):
        return True
    else:
        return False


def get_device():
    dev = None
    devices = map(InputDevice, list_devices())
    for device in devices:
        if device.name == READER_DEVICE:
            dev = InputDevice(device.fn)
    return dev


class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = '/var/run/wheel/barcode-reader.pid'
        self.pidfile_timeout = 5

    def run(self):
        while True:
            logger.info("Getting the device...")
            dev = get_device()

            if dev:
                logger.info("We got the device...")
                dev.grab()
                logger.info("Starting the Barcode Reader daemon...")
                while True:
                    barcode = ""
                    caps = False
                    try:
                        for event in dev.read_loop():
                            if event.type == ecodes.EV_KEY:
                                data = categorize(event)
                                if data.scancode == 42:
                                    # Shift event
                                    if data.keystate == 1:
                                        caps = True
                                    if data.keystate == 0:
                                        caps = False
                                if data.keystate == 1:  # Down events only
                                    if caps:
                                        key_lookup = u'{}'.format(CAPSCODES.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
                                    else:
                                        key_lookup = u'{}'.format(SCANCODES.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
                                    if (data.scancode != 42) and (data.scancode != 28):
                                        barcode += key_lookup
                                    if(data.scancode == 28):
                                        # Enter event
                                        logger.info("Scan: %s" % barcode)
                                        # We have a Barcode (http://gestion.he-arc.ch/quiz/128374A4/)
                                        try:
                                            code = barcode.split('/')[4]
                                        except IndexError:
                                            code = "0"
                                        if validate_code(code):
                                            logger.info("Valid code: %s" % code)
                                            url = "http://localhost/booth/scan/%s/" % code
                                        else:
                                            # The code is invalid, sorry
                                            logger.info("Not valid barcode read: %s" % barcode)
                                            url = "http://localhost/booth/scan/%s/" % code

                                        logger.info("URL: %s" % url)
                                        chromix(url)
                                        barcode = ''
                    except IOError:
                        logger.error("IOError")
                        break
            time.sleep(2)


app = App()

daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve = [handler.stream]
daemon_runner.do_action()

logger.info("Terminating the Barcode Reader daemon...")