#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue 15. Feb CET 2022
@author: Bjoern Kasper (urmel79)
Wrapper class to communicate with the DMM Keysight 34465A via LAN interface and SCPI commands using PyVisa and PyVISA-py
"""
import pyvisa
import time, sys
from enum import Enum

class MeasType(Enum):
    VOLT = "VOLT"
    CURR = "CURR"
    RES  = "RES"
    TEMP = "TEMP"
    FREQ = "FREQ"
    
class TempProbeType(Enum):
    RTD  = "RTD"  # RTD 2-wire
    FRTD = "FRTD" # RTD 4-wire
    TC   = "TC"   # thermocouple
    THER = "THER" # thermistor (NTC) 2-wire
    FTH  = "FTH"  # thermistor (NTC) 4-wire
    
class MeasConfig(object):
    pass

class PyVisa_Keysight_34465A():
    def __init__(self, tcp_ip):
        self._ip = tcp_ip
        self._delay = 0.01 # delay for writing the commands in seconds (10 ms)
        
        try:
            if self._ip == []:
                self.status = "No IP address provided"
            elif self._ip != []:
                self.rm = pyvisa.ResourceManager('@py')
                self.dmm_res = 'TCPIP0::%s::INSTR' %self._ip
                self.dmm = self.rm.open_resource(self.dmm_res)
            
                self.status = "Connected"
                self.connected_with = 'LAN over %s' %self._ip
                
        except pyvisa.VisaIOError:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Pyvisa is not able to connect with the device")
    
    # define a OPEN CONNECTION function
    def openConnection(self, tcp_ip):
        try:
            if self.status == "Disconnected":
                if tcp_ip == []:
                    self.status = "No IP address provided"
                elif tcp_ip != []:
                    self.rm = pyvisa.ResourceManager('@py')
                    self.dmm_res = 'TCPIP0::%s::INSTR' %tcp_ip
                    self.dmm = self.rm.open_resource(self.dmm_res)

                    self.status = "Connected"
                    self.connected_with = 'LAN over %s' %tcp_ip
                    
        except pyvisa.VisaIOError:
            self.status = "Disconnected"
            self.connected_with = "Nothing"
            print("Pyvisa is not able to connect with the device")
    
    # define a CLOSE CONNECTION function
    def closeConnection(self):
        try:
            if self.status == "Connected":
                self.rm.close()
                self.status = "Disconnected"
                self.connected_with = "Nothing"
                
        except pyvisa.VisaIOError:
            self.status = "Error"
            print("Device is not connected")
    
    # define a CONFigure TEMPerature MEASUREment function
    def confTempMeasure(self, measConf):
        if (self.status != "Connected"):
            print("Device is not connected")
            return -1

        # check valid measurement type
        if not isinstance(measConf, MeasConfig):
            raise TypeError("Parameter 'measConf' must be an instance of 'MeasConfig' class")

        # reset device
        self.cmd = '*RST'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        # select temperature measurement
        self.cmd = "FUNC 'TEMP'"
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        # use parameters for RTD (PT100, PT1000, 2-wire or 4-wire)
        if measConf.TProbeType.value == 'RTD' or measConf.TProbeType.value == 'FRTD':
            # configure measurement with given probe type
            self.cmd = "TEMP:TRAN:TYPE %s" %measConf.TProbeType.value
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            
            # configure R_0 for RTD or FRTD
            self.cmd = "TEMP:TRAN:%s:RES %s" %(measConf.TProbeType.value, measConf.TProbeConf)
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
        
        # use parameters for thermocouple
        elif measConf.TProbeType.value == 'TC':
            # configure measurement with thermocouple probe and given type (e.g. K, J, R)
            self.cmd = "CONF:TEMP %s,%s" %(measConf.TProbeType.value, measConf.TProbeConf)
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            
            # set to internal temperature reference
            self.cmd = "TEMP:TRAN:%s:RJUN:TYPE INT" %measConf.TProbeType.value
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            
            
        # use parameters for thermistor (NTC with 5 or 10 kOhm, 2-wire or 4-wire)
        elif measConf.TProbeType.value == 'THER' or measConf.TProbeType.value == 'FTH':
            # configure measurement with thermistor probe
            self.cmd = "CONF:TEMP %s" %(measConf.TProbeType.value)
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            
            # configure R_0 for thermistor probe (NTC with 5 or 10 kOhm)
            self.cmd = "TEMP:TRAN:%s:TYPE %s" %(measConf.TProbeType.value, measConf.TProbeConf)
            self.dmm.write(self.cmd)
            time.sleep(self._delay)

        # select unit °C to be used for all temperature measurements
        self.cmd = 'UNIT:TEMP %s' %measConf.TProbeUnit
        self.dmm.write(self.cmd)
        time.sleep(self._delay)

    # define a GET MEASUREMENT function
    def getMeasurement(self):
        if (self.status != "Connected"):
            print("Device is not connected")
            return -1
        
        # retrieve 1 measurement sample and read it back
        self.cmd = 'SAMP:COUN 1'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        self.cmd = 'READ?'
        self.ret_val = self.dmm.query(self.cmd)
        self.ret_val = float(self.ret_val)
        time.sleep(self._delay)

        return self.ret_val
