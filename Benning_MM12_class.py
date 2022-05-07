#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sa 07. May CET 2022
@author: Bjoern Kasper (urmel79)
Wrapper class 'Benning_MM12_Serial' to communicate with the DMM Benning MM12
"""

import serial
import time

class Benning_MM12_Serial():
    def __init__(self, port):
        self._port = port
        self.MM12_READ_INFOS   = b'\x55\x55\x00\x00\xaa'
        self.MM12_READ_DISPLAY = b'\x55\x55\x01\x00\xab'
        
        try:
            if self._port == []:
                self.status = "Error"
                print("No serial port provided")
            else:
                self._serial = serial.Serial(port=self._port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2)
            
                self.status = "Connected"
                self.connected_with = 'Benning MM12 over USB'
                
        except Exception as ex:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Connecting with the device raised the error: '{}'".format(ex))
        
    # define a separate OPEN CONNECTION function
    def openConnection(self, port):
        self._port = port
        
        try:
            if self.status == "Disconnected":
                if self._port == []:
                    self.status = "Error"
                    print("No serial port provided")
                else:
                    self._serial = serial.Serial(port=self._port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2)

                    self.status = "Connected"
                    self.connected_with = 'Benning MM12 over USB'
                    
        except Exception as ex:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Connecting with the device raised the error: '{}'".format(ex))

    # define a CLOSE CONNECTION function
    def closeConnection(self):
        try:
            if self.status == "Connected":
                self._serial.close()
                self.status = "Disconnected"
                self.connected_with = "Nothing"
                
        except Exception as ex:
            self.status = "Error"
            print("Disconnecting from the device raised the error: '{}'".format(ex))

    # define an internal function to convert hex strings to human readable ones
    def _func_convert_hex_str_human_readable(self, str_in):
        self.hex_string = str_in.hex()
        # fill string with spaces for better reading of the hex string
        self.hex_string_wSpaces = " ".join(self.hex_string[i-1:i+1] for i, c in enumerate(self.hex_string) if i%2)
        return self.hex_string_wSpaces
    
    # define an internal function to convert hex strings to ASCII
    def _func_convert_hex2ascii(self, hex_str):
        # convert hex string to bytes object
        self.bytes_object = bytes.fromhex(hex_str)

        # convert bytes object to ASCII representation
        self.ascii_str = self.bytes_object.decode("ASCII")

        # replace unnecessary characters
        self.ascii_str = self.ascii_str.replace("\x00", "")
        # strip leading and trailing whitespaces
        self.ascii_str = self.ascii_str.strip()

        return self.ascii_str
    
    def _func_convert_hex2int(self, hex_str):
        # convert hex string to bytes object
        self.bytes_object = bytes.fromhex(hex_str)

        # convert hex bytes to integer
        self.out_int = int.from_bytes(self.bytes_object, 'little', signed=False)

        return self.out_int
            
    def getDeviceInfos(self):
        # flush input buffer, discarding all its contents
        self._serial.reset_input_buffer()

        self._serial.write(self.MM12_READ_INFOS)
        
        self.hex_string = self._serial.read(57)
        self.hex_bytes = self.hex_string.hex()
        
        self.dict_dmm_infos = {}
        
        # bytes 0..31 from data payload represent the model name
        self.model_name_hex = self.hex_bytes[8:72]

        self.model_name_str = self._func_convert_hex2ascii(self.model_name_hex)

        self.dict_dmm_infos['model'] = ('Model name', self.model_name_str)
        
        # bytes 32..47 from data payload represent the serial number
        self.serial_number_hex = self.hex_bytes[72:104]

        self.serial_number_str = self._func_convert_hex2ascii(self.serial_number_hex)

        self.dict_dmm_infos['serial'] = ('Serial number', self.serial_number_str)
        
        # bytes 48..49 from data payload represent the model ID
        self.model_ID_hex = self.hex_bytes[104:108]

        self.model_ID_int = self._func_convert_hex2int(self.model_ID_hex)

        self.dict_dmm_infos['id'] = ('Model ID', self.model_ID_int)
        
        # bytes 50..51 from data payload represent the firmware version
        self.firmware_version_hex = self.hex_bytes[108:112]

        self.firmware_version_int = self._func_convert_hex2int(self.firmware_version_hex)

        self.dict_dmm_infos['fw'] = ('Firmware version', self.firmware_version_int/100)
        
        return self.dict_dmm_infos





















