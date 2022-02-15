#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Di 15. Feb CET 2022
@author: Bjoern Kasper (urmel79)
Wrapper class to communicate with the DMM Keysight 34465A via LAN interface and SCPI commands using PyVisa and PyVISA-py
"""
import pyvisa
import time, sys
from enum import Enum

class MeasType(Enum):
    VOLT = "VOLT"
    CURR = "CURR"
    RES = "RES"
    TEMP = "TEMP"
    FREQ = "FREQ"

class PyVisa_Keysight_34465A():
    def __init__(self, tcp_ip):
        self._ip = tcp_ip
        self._delay = 0.01 #delay for writing the commands in seconds (10 ms)
        
        # # define voltage and current limits as constants
        # self.VOLTAGE_MIN     = 0.0
        # self.VOLTAGE_MAX_1_2 = 32.0  # max 32 V
        # self.VOLTAGE_MAX_3   = 5.3   # max 5.3 V

        # self.CURRENT_MIN     = 0.0
        # self.CURRENT_MAX     = 3.2   # max 3.2 A

        # self.OVP_MIN         = 0.001 # min 0.001 V
        # self.OVP_MAX_1_2     = 33.0  # max 33 V
        # self.OVP_MAX_3       = 5.5   # max 5.5 V

        # self.OCP_MIN         = 0.001 # min 0.001 A
        # self.OCP_MAX         = 3.3   # max 3.3 A
        
        try:
            if self._ip == []:
                self.status = "No IP address provided"
            elif self._ip != []:
                self.rm = pyvisa.ResourceManager('@py')
                self.psu_res = 'TCPIP0::%s::INSTR' %self._ip
                self.psu = self.rm.open_resource(self.psu_res)
            
                self.status = "Connected"
                self.connected_with = 'LAN over %s' %self._ip
                
        except pyvisa.VisaIOError:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Pyvisa is not able to connect with the device")
    
    #define a OPEN CONNECTION function
    def openConnection(self, tcp_ip):
        try:
            if self.status == "Disconnected":
                if tcp_ip == []:
                    self.status = "No IP address provided"
                elif tcp_ip != []:
                    self.rm = pyvisa.ResourceManager('@py')
                    self.psu_res = 'TCPIP0::%s::INSTR' %tcp_ip
                    self.psu = self.rm.open_resource(self.psu_res)

                    self.status = "Connected"
                    self.connected_with = 'LAN over %s' %tcp_ip
                    
        except pyvisa.VisaIOError:
            self.status = "Disconnected"
            self.connected_with = "Nothing"
            print("Pyvisa is not able to connect with the device")
    
    #define a CLOSE CONNECTION function
    def closeConnection(self):
        try:
            if self.status == "Connected":
                self.rm.close()
                self.status = "Disconnected"
                self.connected_with = "Nothing"
                
        except pyvisa.VisaIOError:
            self.status = "Error"
            print("Device is not connected")
    
    #define a CONFigure TEMPerature MEASUREment function
    def confTempMeasure(self):
        if (self.status != "Connected"):
            print("Device is not connected")
            return -1

        # reset device
        self.cmd = '*RST'
        self.psu.write(self.cmd)
        time.sleep(self._delay)

        # configure measurement for 4-wire RTD (here an PT100)
        self.cmd = 'CONF:TEMP FRTD,85,1,0.0000001'
        self.psu.write(self.cmd)
        time.sleep(self._delay)

        # select unit °C to be used for all temperature measurements
        self.cmd = 'UNIT:TEMP C'
        self.psu.write(self.cmd)
        time.sleep(self._delay)

    #define a GET MEASUREMENT function
    def getMeasurement(self, measType):
        if (self.status != "Connected"):
            print("Device is not connected")
            return -1

        # # check valid measurement type
        # if not isinstance(measType, MeasType):
        #     raise TypeError("Parameter 'measType' must be an instance of 'MeasType' Enum")

        # trigger the measurement as single shot and retrieve 1 dataset
        self.cmd = 'MEAS:%s?' %measType.value
        self.ret_val = self.psu.query(self.cmd)
        self.ret_val = float(self.ret_val)
        time.sleep(self._delay)

        return self.ret_val
