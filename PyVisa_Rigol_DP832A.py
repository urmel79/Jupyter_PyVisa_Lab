# -*- coding: utf-8 -*-
"""
Created on Mi 12. Jan CET 2022
@author: Bjoern Kasper (urmel79)
Wrapper class to communicate with the Rigol DP832A via LAN interface and SCPI commands using PyVisa and PyVISA-py
"""
import pyvisa
import time, sys

import pyvisa
import time, sys

class PyVisa_Rigol_DP832():
    def __init__(self, tcp_ip):
        self._ip = tcp_ip
        self._delay = 0.01 #delay for writing the commands in seconds (10 ms)
        
        try:
            if self._ip == [] :
                self.status = "No IP address provided"
            elif self._ip != []:
                self.rm = pyvisa.ResourceManager('@py')
                self.psu_res = 'TCPIP0::%s::INSTR' %self._ip
                self.psu = self.rm.open_resource(self.psu_res)
            
                self.status = "Connected"
                self.connected_with = 'LAN'
                
        except VisaIOError:
            self.status = "Not Connected"
            print("Pyvisa is not able to connect with the device")
            
    #define a TOGGLE OUTPUT function
    def toggleOutput(self, chan, state):
        self.cmd1 = ':OUTP CH%s,%s' %(chan, state)
        self.psu.write(self.cmd1)
        time.sleep(self._delay)
        
    #define a SET VOLTAGE function
    def setVoltage(self, chan, voltage):
        self.cmd1 = ':INST:NSEL %s' %chan
        self.cmd2 = ':VOLT %s' %voltage
        self.psu.write(self.cmd1)
        time.sleep(self._delay)
        self.psu.write(self.cmd2)
        time.sleep(self._delay)
        
    #define a SET CURRENT function
    def setCurrent(self, chan, current):
        self.cmd1 = ':INST:NSEL %s' %chan
        self.cmd2 = ':CURR %s' %current
        self.psu.write(self.cmd1)
        time.sleep(self._delay)
        self.psu.write(self.cmd2)
        time.sleep(self._delay)


