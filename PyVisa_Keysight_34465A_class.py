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
    RES = "RES"
    TEMP = "TEMP"
    FREQ = "FREQ"
    
class MeasConfig(object):
    pass

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
                self.dmm_res = 'TCPIP0::%s::INSTR' %self._ip
                self.dmm = self.rm.open_resource(self.dmm_res)
            
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
                    self.dmm_res = 'TCPIP0::%s::INSTR' %tcp_ip
                    self.dmm = self.rm.open_resource(self.dmm_res)

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
        
        if measConf.TProbeType == 'RTD' or measConf.TProbeType == 'FRTD':
            # configure measurement with given probe type
            self.cmd = "TEMP:TRAN:TYPE %s" %measConf.TProbeType
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            
            # configure R_0 for RTD or FRTD
            self.cmd = "TEMP:TRAN:%s:RES %s" %(measConf.TProbeType, measConf.TProbeConf)
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
        
        # use parameters for thermocouple
        elif measConf.TProbeType == 'TC':
            # configure measurement with thermocouple probe and given type (e.g. K, J, R)
            self.cmd = "CONF:TEMP %s,%s" %(measConf.TProbeType, measConf.TProbeConf)
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            
            # set to internal temperature reference
            self.cmd = "TEMP:TRAN:TC:RJUN:TYPE INT"
            self.dmm.write(self.cmd)
            time.sleep(self._delay)

        # select unit °C to be used for all temperature measurements
        self.cmd = 'UNIT:TEMP %s' %measConf.TProbeUnit
        self.dmm.write(self.cmd)
        time.sleep(self._delay)

    #define a GET MEASUREMENT function
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
