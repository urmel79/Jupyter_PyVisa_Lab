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
        self.MM12_READ_INFOS   = '55 55 00 00 AA'
        self.MM12_READ_DISPLAY = '55 55 01 00 AB'
        
        # function codes of Benning MM12 (table 6 in communication datasheet)
        # the codes 0x32 ... 0x3E have not been included at the moment, because they are rarely used
        # dictionary holds measuring modes and the corresponding SI base units
        self.dict_function_codes_units = {
            0x00 : ('None', 'None'),
            0x01 : ('AC V', 'V'),
            0x02 : ('DC V', 'V'),
            0x03 : ('AC mV', 'mV'),
            0x04 : ('DC mV', 'mV'),
            0x05 : ('Ohm', 'Ohm'),
            0x06 : ('Continuity', 'Ohm'),
            0x07 : ('Diode', 'V'),
            0x08 : ('Capacitor', 'uF'),
            0x09 : ('AC A', 'A'),
            0x0A : ('DC A', 'A'),
            0x0B : ('AC mA', 'mA'),
            0x0C : ('DC mA', 'mA'),
            0x0D : ('°C', '°C'),
            0x0E : ('°F', '°F'),
            0x0F : ('Frequency', 'Hz'),
            0x10 : ('Duty', 'sec'),
            0x11 : ('Hz (V)', 'Hz'),
            0x12 : ('Hz (mV)', 'Hz'),
            0x13 : ('Hz (A)', 'Hz'),
            0x14 : ('Hz (mA)', 'Hz'),
            0x15 : ('AC+DC (V)', 'V'),
            0x16 : ('AC+DC (mV)', 'mV'),
            0x17 : ('AC+DC (A)', 'A'),
            0x18 : ('AC+DC (mA)', 'mA'),
            0x19 : ('LPF (V)', 'V'),
            0x1A : ('LPF (mV)', 'mV'),
            0x1B : ('LPF (A)', 'A'),
            0x1C : ('LPF (mA)', 'mA'),
            0x1D : ('AC uA', 'uA'),
            0x1E : ('DC uA', 'uA'),
            0x1F : ('DC A out', 'A'),
            0x20 : ('DC A out (Slow Linear)', 'A'),
            0x21 : ('DC A out (Fast Linear)', 'A'),
            0x22 : ('DC A out (Slow Step)', 'A'),
            0x23 : ('DC A out (Fast Step)', 'A'),
            0x24 : ('Loop Power', 'W'),
            0x25 : ('250 Ohm HART', 'Ohm'),
            0x26 : ('Voltage Sense', 'V'),
            0x27 : ('Peak Hold (V)', 'V'),
            0x28 : ('Peak Hold (mV)', 'mV'),
            0x29 : ('Peak Hold (A)', 'A'),
            0x2A : ('Peak Hold (mA)', 'mA'),
            0x2B : ('LoZ AC V', 'V'),
            0x2C : ('LoZ DC V', 'V'),
            0x2D : ('LoZ AC+DC (V)', 'V'),
            0x2E : ('LoZ LPF (V)', 'V'),
            0x2F : ('LoZ Hz (V)', 'V'),
            0x30 : ('LoZ Peak Hold (V)', 'V'),
            0x31 : ('Battery', '%')
        }
        
        # range codes of Benning MM12 (table 7.1 and 7.2 in communication datasheet)
        self.list_range_multiplier_ohm = {
            0x00 : 0.01,
            0x01 : 0.1,
            0x02 : 1,
            0x03 : 10,
            0x04 : 100,
            0x05 : 1000
        }

        self.list_range_multiplier_temp = {
            0x00 : 0.1
        }

        self.list_range_multiplier_voltage = {
            0x00 : 0.0001,
            0x01 : 0.001,
            0x02 : 0.01,
            0x03 : 0.1
        }

        # Attention: these hexadecimal values are actually implemented like this in the DMM firmware!
        self.list_range_multiplier_LoZ_voltage = {
            0x02 : 0.01,
            0x03 : 0.1
        }

        self.list_range_multiplier_millivoltage = {
            0x00 : 0.001,
            0x01 : 0.01
        }

        # Attention: these hexadecimal values are actually implemented like this in the DMM firmware!
        self.list_range_multiplier_current = {
            0x02 : 0.0001,
            0x03 : 0.001
        }

        self.list_range_multiplier_millicurrent = {
            0x00 : 0.001,
            0x01 : 0.01
        }

        self.list_range_multiplier_capacity = {
            0x00 : 0.00001,
            0x01 : 0.0001,
            0x02 : 0.001,
            0x03 : 0.01,
            0x04 : 0.1,
            0x05 : 1,
            0x06 : 10
        }

        self.list_range_multiplier_frequency = {
            0x00 : 0.01,
            0x01 : 0.1,
            0x02 : 1,
            0x03 : 10
        }

        self.list_range_multiplier_continuity = {
            0x00 : 0.01
        }

        self.list_range_multiplier_diode = {
            0x00 : 0.001
        }

        self.list_range_multiplier_NONE = {
            0x00 : 1
        }
        
        # scope codes of Benning MM12 (table 2 in communication datasheet)
        # bits 7..3 represent the unit
        self.list_scope_unit = {
            0x00 : 'None',
            0x01 : 'V',
            0x02 : 'mV',
            0x03 : 'A',
            0x04 : 'mA',
            0x05 : 'dB',
            0x06 : 'dBm',
            0x07 : 'mF',
            0x08 : 'uF',
            0x09 : 'nF',
            0x0A : 'GOhm',
            0x0B : 'MOhm',
            0x0C : 'kOhm',
            0x0D : 'Ohm',
            0x0E : '%',
            0x0F : 'MHz',
            0x10 : 'kHz',
            0x11 : 'Hz',
            0x12 : '°C',
            0x13 : '°F',
            0x14 : 'sec',
            0x15 : 'ms',
            0x16 : 'us',
            0x17 : 'ns',
            0x18 : 'uA',
            0x19 : 'min',
            0x1A : 'kW',
            0x1B : 'PF'
        }

        # bits 2..0 represent the multiplier
        self.list_scope_multiplier = {
            0x00 : None,
            0x01 : 0.1,
            0x02 : 0.01,
            0x03 : 0.001,
            0x04 : 0.0001
        }
        
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

    # define an internal function to convert byte strings to byte
    def _func_convert_byteString_2_bytes(self, str_in):
        # remove whitespaces separating the hex bytes
        self.hex_str = str_in.replace(" ", "")

        self.hex_bytes = bytes.fromhex(self.hex_str)

        return self.hex_bytes
            
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
    
    # define an internal function to convert hex strings to integers
    def _func_convert_hex2int(self, hex_str):
        # convert hex string to bytes object
        self.bytes_object = bytes.fromhex(hex_str)

        # convert hex bytes to integer
        self.out_int = int.from_bytes(self.bytes_object, 'little', signed=False)

        return self.out_int
    
    # define an internal function to mask the most significant bit (MSB)
    def _func_mask_MSB(self, byte_in):
        byte_out = byte_in & 0b01111111
        return byte_out
    
    # define a function to retrieve the device infos and return a dictionary
    def getDeviceInfos(self):
        # flush input buffer, discarding all its contents
        self._serial.reset_input_buffer()

        # convert byte string of command to bytes
        self.hex_bytes = self._func_convert_byteString_2_bytes(self.MM12_READ_INFOS)
        self._serial.write(self.hex_bytes)
        
        # read back the 57 byte response of the MM12
        self.hex_string = self._serial.read(57)
        self.hex_bytes = self.hex_string.hex()
        
        ###
        # test for valid response
        self.cmd_response = self.hex_bytes[0:8]
        self.cmd_response_int = int(self.cmd_response, 16)
        
        if self.cmd_response_int != 0x55550034:
            print('Reading failed!')
            return {}
        
        self.dict_dmm_infos = {}
        
        ###
        # bytes 0..31 from data payload represent the model name
        self.model_name_hex = self.hex_bytes[8:72]

        self.model_name_str = self._func_convert_hex2ascii(self.model_name_hex)

        self.dict_dmm_infos['model'] = ('Model name', self.model_name_str)
        
        ###
        # bytes 32..47 from data payload represent the serial number
        self.serial_number_hex = self.hex_bytes[72:104]

        self.serial_number_str = self._func_convert_hex2ascii(self.serial_number_hex)

        self.dict_dmm_infos['serial'] = ('Serial number', self.serial_number_str)
        
        ###
        # bytes 48..49 from data payload represent the model ID
        self.model_ID_hex = self.hex_bytes[104:108]

        self.model_ID_int = self._func_convert_hex2int(self.model_ID_hex)

        self.dict_dmm_infos['id'] = ('Model ID', self.model_ID_int)
        
        ###
        # bytes 50..51 from data payload represent the firmware version
        self.firmware_version_hex = self.hex_bytes[108:112]

        self.firmware_version_int = self._func_convert_hex2int(self.firmware_version_hex)

        self.dict_dmm_infos['fw'] = ('FW version', self.firmware_version_int/100)
        
        return self.dict_dmm_infos

    # define a function to retrieve the measurements converted in SI base units
    def getMeasurement_baseUnits(self):
        # flush input buffer, discarding all its contents
        self._serial.reset_input_buffer()
        
        # convert byte string of command to bytes
        self.hex_bytes = self._func_convert_byteString_2_bytes(self.MM12_READ_DISPLAY)
        self._serial.write(self.hex_bytes)
        
        # read back the 17 byte response of the MM12
        self.hex_string = self._serial.read(17)
        self.hex_bytes = self.hex_string.hex()
        
        ###
        # test for valid response
        self.cmd_response = self.hex_bytes[0:8]
        self.cmd_response_int = int(self.cmd_response, 16)
        
        if self.cmd_response_int != 0x5555010C:
            print('Reading failed!')
            return {}
        
        self.dict_dmm_measurement = {}
        
        ###
        # byte 0 from data payload is the function code
        self.func_code = self.hex_bytes[8:10]
        # convert from hex to int
        self.func_code_int = int(self.func_code, 16)

        # mask the MSB that identifies the auto or manual test
        self.func_code_int = self._func_mask_MSB(self.func_code_int)

        self.list_func_unit = self.dict_function_codes_units[self.func_code_int]
        
        ###
        # byte 1 from data payload is the range code
        self.range_code = self.hex_bytes[10:12]
        # convert from hex to int
        self.range_code_int = int(self.range_code, 16)

        # mask the MSB that identifies the auto or manual range
        self.range_code_int = self._func_mask_MSB(self.range_code_int)

        # function: Ohm
        if self.func_code_int == 0x05:
            self.range_float = self.list_range_multiplier_ohm[self.range_code_int]

        # function: Temperature (°C or °F)
        elif ( self.func_code_int == 0x0D or 
                self.func_code_int == 0x0E ):
            self.range_float = self.list_range_multiplier_temp[self.range_code_int]

        # function: Voltage (AC V, LPF (V), Peak Hold (V), DC V, AC+DC (V))
        elif ( self.func_code_int == 0x01 or
                self.func_code_int == 0x19 or
                self.func_code_int == 0x27 or
                self.func_code_int == 0x02 or
                self.func_code_int == 0x15 ):
            self.range_float = self.list_range_multiplier_voltage[self.range_code_int]

        # function: Millivoltage (AC mV, LPF (mV), Peak Hold (mV), DC mV, AC+DC (mV))
        elif ( self.func_code_int == 0x03 or
                self.func_code_int == 0x1A or
                self.func_code_int == 0x28 or
                self.func_code_int == 0x04 or
                self.func_code_int == 0x16 ):
            self.range_float = self.list_range_multiplier_millivoltage[self.range_code_int]

        # function: LoZ Voltage (LoZ AC V, LoZ DC V)
        elif ( self.func_code_int == 0x2B or
                self.func_code_int == 0x2C ):
            self.range_float = self.list_range_multiplier_LoZ_voltage[self.range_code_int]

        # function: Current (AC A, DC A, AC+DC (A), LPF (A), Peak Hold (A))
        elif ( self.func_code_int == 0x09 or
                self.func_code_int == 0x0A or
                self.func_code_int == 0x17 or
                self.func_code_int == 0x1B or
                self.func_code_int == 0x29 ):
            self.range_float = self.list_range_multiplier_current[self.range_code_int]

        # function: Millicurrent (AC mA, DC mA, AC+DC (mA), LPF (mA), Peak Hold (mA))
        elif ( self.func_code_int == 0x0B or
                self.func_code_int == 0x0C or
                self.func_code_int == 0x18 or
                self.func_code_int == 0x1C or
                self.func_code_int == 0x2A ):
            self.range_float = self.list_range_multiplier_millicurrent[self.range_code_int]

        # function: Capacitor (in µF)
        elif self.func_code_int == 0x08:
            self.range_float = self.list_range_multiplier_capacity[self.range_code_int]

        # function: Frequency (Hz (V), Hz (mV), Hz (A), Hz (mA))
        elif ( self.func_code_int == 0x11 or
                self.func_code_int == 0x12 or
                self.func_code_int == 0x13 or
                self.func_code_int == 0x14 ):
            self.range_float = self.list_range_multiplier_frequency[self.range_code_int]

        # function: Continuity (Ohm)
        elif self.func_code_int == 0x06:
            self.range_float = self.list_range_multiplier_continuity[self.range_code_int]

        # function: Diode (V)
        elif self.func_code_int == 0x07:
            self.range_float = self.list_range_multiplier_continuity[self.range_code_int]

        # function: NONE
        elif self.func_code_int == 0x00:
            self.range_float = self.list_range_multiplier_NONE[self.range_code_int]
        
        ###
        # bytes 2..4 from data payload are the measuring value (24bit signed integer)
        self.disp_value_hex = self.hex_bytes[12:18]
        
        self.disp_value_sint = self._func_convert_hex2int(self.disp_value_hex)
        
        self.dict_dmm_measurement['function'] = self.list_func_unit[0]
        self.dict_dmm_measurement['value'] = self.disp_value_sint*self.range_float
        self.dict_dmm_measurement['unit'] = self.list_func_unit[1]
        
        return self.dict_dmm_measurement
    
    # define a function to retrieve the measurements converted in human readable units
    def getMeasurement_humanUnits(self):
        # flush input buffer, discarding all its contents
        self._serial.reset_input_buffer()

        # convert byte string of command to bytes
        self.hex_bytes = self._func_convert_byteString_2_bytes(self.MM12_READ_DISPLAY)
        self._serial.write(self.hex_bytes)
        
        # read back the 17 byte response of the MM12
        self.hex_string = self._serial.read(17)
        self.hex_bytes = self.hex_string.hex()
        
        ###
        # test for valid response
        self.cmd_response = self.hex_bytes[0:8]
        self.cmd_response_int = int(self.cmd_response, 16)
        
        if self.cmd_response_int != 0x5555010C:
            print('Reading failed!')
            return {}
        
        self.dict_dmm_measurement = {}
        
        ###
        # bytes 2..4 from data payload are the measuring value (24bit signed integer)
        self.disp_value_hex = self.hex_bytes[12:18]
        
        self.disp_value_sint = self._func_convert_hex2int(self.disp_value_hex)
        
        ###
        # byte 5 from data payload represent the scope code
        self.scope_code_hex = self.hex_bytes[18:20]
        # convert from hex to int
        self.scope_code_int = int(self.scope_code_hex, 16)

        ###
        # byte 5, bits 7..3 represent the unit
        self.unit_code = self.scope_code_int >> 3
        self.unit_str = self.list_scope_unit[self.unit_code]

        ###
        # byte 5, bits 2..0 represent the multiplier
        self.multiplier_code = self.scope_code_int & 0b00000111
        self.multiplier_float = self.list_scope_multiplier[self.multiplier_code]
        
        self.dict_dmm_measurement['value'] = self.disp_value_sint*self.multiplier_float
        self.dict_dmm_measurement['unit'] = self.unit_str
        
        return self.dict_dmm_measurement



















