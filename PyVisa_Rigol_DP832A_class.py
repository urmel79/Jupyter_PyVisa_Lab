#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mi 12. Jan CET 2022
@author: Bjoern Kasper (urmel79)
Wrapper class to communicate with the Rigol DP832A via LAN interface and SCPI commands using PyVisa and PyVISA-py
"""
import pyvisa
import time, sys

class PyVisa_Rigol_DP832A():
    def __init__(self, tcp_ip):
        self._ip = tcp_ip
        self._delay = 0.01 #delay for writing the commands in seconds (10 ms)
        
        # define voltage and current limits as constants
        self.VOLTAGE_MIN     = 0.0
        self.VOLTAGE_MAX_1_2 = 32.0  # max 32 V
        self.VOLTAGE_MAX_3   = 5.3   # max 5.3 V

        self.CURRENT_MIN     = 0.0
        self.CURRENT_MAX     = 3.2   # max 3.2 A

        self.OVP_MIN         = 0.001 # min 0.001 V
        self.OVP_MAX_1_2     = 33.0  # max 33 V
        self.OVP_MAX_3       = 5.5   # max 5.5 V

        self.OCP_MIN         = 0.001 # min 0.001 A
        self.OCP_MAX         = 3.3   # max 3.3 A
        
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
    
    #define a TOGGLE OUTPUT function
    def toggleOutput(self, chan, state):
        if (self.status == "Connected"):
            if ((chan == 1) or (chan == 2) or (chan == 3)):
                if ((state == 'ON') or (state == 'OFF')):
                    self.cmd1 = ':OUTP CH%s,%s' %(chan, state)
                    self.psu.write(self.cmd1)
                    time.sleep(self._delay)
                    return chan, state
                else:
                    print("Wrong state provided <'ON'|'OFF'>")
                    return -1
            else:
                print("Wrong channel selected <1|2|3>")
                return -1
        else:
            print("Device is not connected")
            return -1
    
    #define a SET VOLTAGE function
    def setVoltage(self, chan, voltage):
        if (self.status == "Connected"):
            if ((chan == 1) or (chan == 2) or (chan == 3)):
                # check voltage limits
                if (voltage < self.VOLTAGE_MIN): voltage = self.VOLTAGE_MIN
                if ((chan == 1) or (chan == 2)):
                    if (voltage > self.VOLTAGE_MAX_1_2): voltage = self.VOLTAGE_MAX_1_2
                elif (chan == 3):
                    if (voltage > self.VOLTAGE_MAX_3): voltage = self.VOLTAGE_MAX_3
                
                self.chan_curr = self.psu.query(':INST:NSEL?')
                if (self.chan_curr != chan):
                    self.cmd1 = ':INST:NSEL %s' %chan
                
                self.cmd2 = ':VOLT %s' %voltage
                self.psu.write(self.cmd1)
                time.sleep(self._delay)
                self.psu.write(self.cmd2)
                time.sleep(self._delay)
                return chan, voltage
            else:
                print("Wrong channel selected <1|2|3>")
                return -1
        else:
            print("Device is not connected")
            return -1
        
    #define a SET CURRENT function
    def setCurrent(self, chan, current):
        if self.status == "Connected":
            if ((chan == 1) or (chan == 2) or (chan == 3)):
                # check current limits
                if (current < self.CURRENT_MIN): current = self.CURRENT_MIN
                if (current > self.CURRENT_MAX): current = self.CURRENT_MAX
                
                self.chan_curr = self.psu.query(':INST:NSEL?')
                if (self.chan_curr != chan):
                    self.cmd1 = ':INST:NSEL %s' %chan
                
                self.cmd2 = ':CURR %s' %current
                self.psu.write(self.cmd1)
                time.sleep(self._delay)
                self.psu.write(self.cmd2)
                time.sleep(self._delay)
                return chan, current
            else:
                print("Wrong channel selected <1|2|3>")
                return -1
        else:
            print("Device is not connected")
            return -1
        
    #define a SET OVERVOLTAGE PROTECTION function
    def setOVP(self, chan, ovp):
        if self.status == "Connected":
            if ((chan == 1) or (chan == 2) or (chan == 3)):
                # check ovp limits
                if (ovp < self.OVP_MIN): ovp = self.OVP_MIN
                if ((chan == 1) or (chan == 2)):
                    if (ovp > self.OVP_MAX_1_2): ovp = self.OVP_MAX_1_2
                elif (chan == 3):
                    if (ovp > self.OVP_MAX_3): ovp = self.OVP_MAX_3
                
                self.chan_curr = self.psu.query(':INST:NSEL?')
                if (self.chan_curr != chan):
                    self.cmd1 = ':INST:NSEL %s' %chan

                self.cmd2 = ':VOLT:PROT %s' %ovp
                self.psu.write(self.cmd1)
                time.sleep(self._delay)
                self.psu.write(self.cmd2)
                time.sleep(self._delay)
                return chan, ovp
            else:
                print("Wrong channel selected <1|2|3>")
                return -1
        else:
            print("Device is not connected")
            return -1

    #define a TOGGLE OVERVOLTAGE PROTECTION function
    def toggleOVP(self, chan, state):
        if self.status == "Connected":
            if ((chan == 1) or (chan == 2) or (chan == 3)):
                if ((state == 'ON') or (state == 'OFF')):
                    self.chan_curr = self.psu.query(':INST:NSEL?')
                    if (self.chan_curr != chan):
                        self.cmd1 = ':INST:NSEL %s' %chan
                    
                    self.cmd2 = ':VOLT:PROT:STAT %s' %state
                    self.psu.write(self.cmd1)
                    time.sleep(self._delay)
                    self.psu.write(self.cmd2)
                    time.sleep(self._delay)
                    return chan, state
                else:
                    print("Wrong state provided <'ON'|'OFF'>")
                    return -1
            else:
                print("Wrong channel selected <1|2|3>")
                return -1
        else:
            print("Device is not connected")
            return -1

    #define a SET OVERCURRENT PROTECTION function
    def setOCP(self, chan, ocp):
        if self.status == "Connected":
            if ((chan == 1) or (chan == 2) or (chan == 3)):
                # check ocp limits
                if (ocp < self.OCP_MIN): ocp = self.OCP_MIN
                if (ocp > self.OCP_MAX): ocp = self.OCP_MAX
                
                self.chan_curr = self.psu.query(':INST:NSEL?')
                if (self.chan_curr != chan):
                    self.cmd1 = ':INST:NSEL %s' %chan
                
                self.cmd2 = ':CURR:PROT %s' %ocp
                self.psu.write(self.cmd1)
                time.sleep(self._delay)
                self.psu.write(self.cmd2)
                time.sleep(self._delay)
                return chan, ocp
            else:
                print("Wrong channel selected <1|2|3>")
                return -1
        else:
            print("Device is not connected")
            return -1

    #define a TOGGLE OVERCURRENT PROTECTION function
    def toggleOCP(self, chan, state):
        if self.status == "Connected":
            if ((chan == 1) or (chan == 2) or (chan == 3)):
                if ((state == 'ON') or (state == 'OFF')):
                    self.chan_curr = self.psu.query(':INST:NSEL?')
                    if (self.chan_curr != chan):
                        self.cmd1 = ':INST:NSEL %s' %chan
                    
                    self.cmd2 = ':CURR:PROT:STAT %s' %state
                    self.psu.write(self.cmd1)
                    time.sleep(self._delay)
                    self.psu.write(self.cmd2)
                    time.sleep(self._delay)
                    return chan, state
                else:
                    print("Wrong state provided <'ON'|'OFF'>")
                    return -1
            else:
                print("Wrong channel selected <1|2|3>")
                return -1
        else:
            print("Device is not connected")
            return -1
        
    #define a MEASURE VOLTAGE function
    def measVolt(self, chan):
        if self.status == "Connected":
            if ((chan == 1) or (chan == 2) or (chan == 3)):
                self.cmd1 = ':MEAS:VOLT? CH%s' %chan
                self.V = self.psu.query(self.cmd1)
                self.V = float(self.V)
                time.sleep(self._delay)
                return chan, self.V
            else:
                print("Wrong channel selected <1|2|3>")
                return -1
        else:
            print("Device is not connected")
            return -1
    
    #define a MEASURE CURRENT function
    def measCurrent(self, chan):
        if self.status == "Connected":
            if ((chan == 1) or (chan == 2) or (chan == 3)):
                self.cmd1 = ':MEAS:CURR? CH%s' %chan
                self.C = self.psu.query(self.cmd1)
                self.C = float(self.C)
                time.sleep(self._delay)
                return chan, self.C
            else:
                print("Wrong channel selected <1|2|3>")
                return -1
        else:
            print("Device is not connected")
            return -1

    #define a MEASURE POWER function
    def measPower(self, chan):
        if self.status == "Connected":
            if ((chan == 1) or (chan == 2) or (chan == 3)):
                self.cmd1 = ':MEAS:POWE? CH%s' %chan
                self.P = self.psu.query(self.cmd1)
                self.P = float(self.P)
                time.sleep(self._delay)
                return chan, self.P
            else:
                print("Wrong channel selected <1|2|3>")
                return -1
        else:
            print("Device is not connected")
            return -1


