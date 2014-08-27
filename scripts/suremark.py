# -*- coding: UTF-8 -*-
# suremark.py
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


from HTMLParser import HTMLParser
import serial
from binascii import unhexlify, hexlify

# Define HEX for formatting
doubleh = '1B68'    # <dh></dh>
doublew = '1B57'    # <dw></dw>
underline = '1B2D'  # <u></u>
overline = '1B5F'    # <o></o>
invert = '1B48'       # <i></i>
bold = '1B47'         # <b></b>
left = '1B6100'
center = '1B6101'
right = '1B6102'
col = '1B6104'
br = '0A'
cut = '1B69'
setfont = '1B21'
fontA = '00'
fontB = '10'
fontC = '01'

# Define HEX for setup
download = '1D3A'
barcode = '1D6B'
message = '1D5E'
logo = '1D2F'
on = '01'
off = '00'

class SuremarkParser(HTMLParser):
    
    hexstring = ""
    
    def handle_starttag(self, tag, attrs):
        if tag == "big":
            self.hexstring += doubleh + on
        elif tag == "em":
            self.hexstring += doublew + on
        elif tag == "u":
            self.hexstring += underline + on
        elif tag == "o":
            self.hexstring += overline + on
        elif tag == "b":
            self.hexstring += bold + on
        elif tag == "r":
            self.hexstring += invert + on
        elif tag == "left":
            self.hexstring += left
        elif tag == "right":
            self.hexstring += right
        elif tag == "center":
            self.hexstring += center
        elif tag == "col":
            self.hexstring += col
        elif tag == "br":
            self.hexstring += br
        elif tag == "cut":
            self.hexstring += cut
        elif tag == "font":
            if attrs[0][1] == 'A':
                self.hexstring += setfont + fontA
            elif attrs[0][1] == 'B':
                self.hexstring += setfont + fontB
            elif attrs[0][1] == 'C':
                self.hexstring += setfont + fontC
        elif tag == "barcode":
            type='04'
            text='00'
            hsize='3'
            height='162'
            data='12345678'
            for a in attrs:
                if a[0] == 'type':
                    type = a[1]
                elif a[0] == 'text':
                    text = a[1]
                elif a[0] == 'hsize':
                    hsize = a[1]
                elif a[0] == 'height':
                    height = a[1]
                elif a[0] == 'data':
                    data = a[1]
            self.hexstring += self.barcode(type, text, hsize, height, data)
        elif tag == "message":
            if attrs[0][1]:
                self.hexstring += message + '0' + str(attrs[0][1]) + '00'
        elif tag == "logo":
            if attrs[0][1]:
                self.hexstring += logo + '000' + str(attrs[0][1]) + '00'

    def handle_data(self, data):
        self.hexstring += hexlify(data.encode('cp850'))
    
    def handle_endtag(self, tag):
        if tag == "big":
            self.hexstring += doubleh + off
        elif tag == "em":
            self.hexstring += doublew + off
        elif tag == "u":
            self.hexstring += underline + off
        elif tag == "o":
            self.hexstring += overline + off
        elif tag == "b":
            self.hexstring += bold + off
        elif tag == "r":
            self.hexstring += invert + off

    def barcode(self, type, text, hsize, height, data):
        bc = '1D6B' + type
        bchsize = '1D770' + hsize
        bcheight = '1D68' + str(hex(int(height))[2:])
        bctext = '1D48' + text
        data = hexlify(data)
        hexbarcode = bchsize + bcheight + bctext + bc + data + '00'
        return hexbarcode

    def getString(self):
        return self.hexstring

def printhex(hexstring):
    ser = serial.Serial(0)
    ser.write(unhexlify(hexstring))
    ser.close()

def printpos(htmlstring):
    sm = SuremarkParser()
    sm.feed(htmlstring)
    printhex(sm.getString())

##def clrmessages():
##    printpos(unhexlify('1B2302'))
##    return
##
##def dowmessage(id, msg):
##    hexid = download +'0' + str(id)
##    printpos(unhexlify(hexid) + msg + unhexlify(download))
##    return 


def postest():
    data = '<b><big>Debian</big> is a free operating system (OS)</b> for your computer. An <r>operating system</r> is the set of <u>basic programs and utilities</u> that make your computer run. <b><em>Debian</em></b> uses the Linux kernel (the core of an operating system), but most of the basic OS tools come from the GNU project; hence the name GNU/Linux.'
    dataB = '<b>Debian is a free operating system (OS)</b> for your computer. An <r>operating system</r> is the set of <u>basic programs and utilities</u> that make your computer run. <b><em>Debian</em></b> uses the Linux kernel (the core of an operating system), but most of the basic OS tools come from the GNU project; hence the name GNU/Linux.'
    string = ''
    string += "<logo id='3'>"
    string += "<font face='A'><center>Font A<left><br>"
    string += data
    string += '<br><br>'
    string += "<font face='B'><center>Font B<left><br>"
    string += dataB
    string += '<br><br>'
    string += "<font face='C'><center>Font C<left><br>"
    string += data
    string += '<br><br>Une string accentuée juste là pour tester tout ça<br><br>'
    string += "<font face='A'><center><barcode><br><left>"
    string += "<message id='2'><cut>"
    printpos(string)