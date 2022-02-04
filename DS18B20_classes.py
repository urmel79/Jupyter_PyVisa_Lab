#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sa 29. Jan CET 2022
@author: Bjoern Kasper (urmel79)
Wrapper classes 'DS18B20_over_USB' and 'DS18B20_over_GPIO' to communicate with the temperature sensor DS18B20
"""

import hid # from packet 'hidapi'
import time, os, subprocess

class DS18B20_over_USB():
    def __init__(self, vid, pid):
        self._vid = vid
        self._pid = pid
        
        try:
            if self._vid == [] or self._pid == []:
                self.status = "Error"
                print("No vendor or product ID provided")
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

####################################################

class DS18B20_over_GPIO():    
    def __init__(self):
        # initialize internal variables
        self._sensor_device_path = '/sys/bus/w1/devices/'
        self._sensor_id_list = []
        self._temperature = 0
    
    # define a GET SENSOR IDs function (detect the connected sensor(s))
    def getSensorIDs(self):
        if self._sensor_id_list == []:
            for self._obj in os.scandir(self._sensor_device_path):
                # sensor IDs start with '28'
                if self._obj.is_dir() and self._obj.name.split("-")[0] == "28":
                    self._sensor_id_list.append(self._obj.name)
                
        return self._sensor_id_list
    
    # define a GET TEMPERATURE BY ID function
    def getTemperatureByID(self, sensor_id):
        if not sensor_id:
            print('No valid sensor ID provided')
            return -1
        
        try:
            self._file_handle = open(self._sensor_device_path + sensor_id + '/temperature')
            self._temperature = float(self._file_handle.read()) / 1000
            self._file_handle.close()
                
            return self._temperature
    
        except Exception as ex:
            print('Reading from the DS18B20 sensors raised the error: "{}"'.format(ex))
    
    # define a GET RESOLUTION BY ID function
    def getResolutionByID(self, sensor_id):
        if not sensor_id:
            print('No valid sensor ID provided')
            return -1
        
        try:
            self._file_handle = open(self._sensor_device_path + sensor_id + '/resolution')
            self._resolution = self._file_handle.read()
            self._resolution = self._resolution.rstrip('\n') # remove trailing newline from resolution
            self._file_handle.close()
                
            return self._resolution
    
        except Exception as ex:
            print('Reading from the DS18B20 sensors raised the error: "{}"'.format(ex))
    
    # define a SET RESOLUTION BY ID AS SUDO function
    def setResolutionByIDAsSudo(self, sensor_id, resolution):
        if not sensor_id or not resolution:
            print('No valid sensor ID or resolution provided')
            return -1
        
        self._file_path = self._sensor_device_path + sensor_id + '/resolution'

        self._command_str = 'sudo sh -c "echo {:d} > {:s}"'.format(resolution, self._file_path)
        self._ret = subprocess.run([self._command_str], shell=True)

        return self._ret