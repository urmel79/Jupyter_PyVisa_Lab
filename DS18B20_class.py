#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sa 29. Jan CET 2022
@author: Bjoern Kasper (urmel79)
Wrapper class to communicate with the temperature sensor DS18B20
"""

import hid # from packet 'hidapi'
import time

class DS18B20_over_USB():
    def __init__(self, vid, pid):
        self._vid = vid
        self._pid = pid
        
        try:
            if self._vid == [] or self._pid == []:
                self.status = "No vendor or product ID provided"
            elif self._vid != [] and self._pid != []:
                self._h = hid.device()
                self._h.open(self._vid, self._pid)
            
                self.status = "Connected"
                self.connected_with = '{:s} ({:s}) with idVendor={:#06x} and idProduct={:#06x} over USB'.format(
                                        self._h.get_product_string(), self._h.get_manufacturer_string(), self._vid, self._pid)
                
        except Exception as ex:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Connecting with the device raised the error: '{}'".format(ex))
        
    # define a separate OPEN CONNECTION function
    def openConnection(self, vid, pid):
        self._vid = vid
        self._pid = pid
        
        try:
            if self.status == "Disconnected":
                if self._vid == [] or self._pid == []:
                    self.status = "No vendor or product ID provided"
                elif self._vid != [] and self._pid != []:
                    self._h = hid.device()
                    self._h.open(self._vid, self._pid)

                    self.status = "Connected"
                    self.connected_with = '{:s} ({:s}) with idVendor={:#06x} and idProduct={:#06x} over USB'.format(
                                            self._h.get_product_string(), self._h.get_manufacturer_string(), self._vid, self._pid)
                    
        except Exception as ex:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Connecting with the device raised the error: '{}'".format(ex))

    # define a CLOSE CONNECTION function
    def closeConnection(self):
        try:
            if self.status == "Connected":
                self._h.close()
                self.status = "Disconnected"
                self.connected_with = "Nothing"
                
        except Exception as ex:
            self.status = "Error"
            print("Disconnecting from the device raised the error: '{}'".format(ex))

    # define a GET SENSOR IDs function (detect the connected sensor(s))
    def getSensorIDs(self):
        self.byte_list = self._h.read(64)

        # how many sensors do we have?
        self.sensors_cnt = self.byte_list[0]
        
        # initialize the array with the number of elements corresponding to the number of sensors
        self.sensor_ids_array = []
        self.sensor_ids_array = [0 for i in range(self.sensors_cnt)]
        
        for self.i in range(1, self.sensors_cnt+1, 1):
            # get current number of sensor
            self.byte_list = self._h.read(64)
            self.sensor_number = self.byte_list[1]
            
            self.sensor_id = ''
            # get sensor ID with the bytes 8 to 16 from character buffer
            for self.j in range(8, 16, 1):
                # convert integer from byte list to string with padding
                self.hex_string = '{:02x}'.format(self.byte_list[self.j])
                self.sensor_id = self.sensor_id + self.hex_string + ' '
            
            self.sensor_id = self.sensor_id.rstrip(None) # remove trailing whitespace from sensor id
            self.sensor_ids_array[self.sensor_number-1] = self.sensor_id
            
        return self.sensor_ids_array
    
    # define a GET TEMPERATURE function for reading the values from all sensors to a dictionary
    def getTemperature_dict(self):
        self.byte_list = self._h.read(64)

        # how many sensors do we have?
        self.sensors_cnt = self.byte_list[0]
        
        # initialize the dictionary
        self.temp_dict = dict()
        
        for self.i in range(1, self.sensors_cnt+1, 1):
            self.byte_list = self._h.read(64)
        
            self.sensor_id = ''
            # get sensor ID with the bytes 8 to 16 from character buffer
            for self.j in range(8, 16, 1):
                # convert integer from byte list to string with padding
                self.hex_string = '{:02x}'.format(self.byte_list[self.j])
                self.sensor_id = self.sensor_id + self.hex_string + ' '
            
            self.sensor_id = self.sensor_id.rstrip(None) # remove trailing whitespace from sensor id
            
            # combine high and low byte of temperature value and convert to float
            self.temp = float(self.byte_list[5] << 8 | self.byte_list[4]) / 10
            
            # add values to temperature dictionary
            self.temp_dict[self.sensor_id] = self.temp
            
        return self.temp_dict
        