#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue 15. Feb CET 2022
@author: Bjoern Kasper (urmel79)
Wrapper class to communicate with the DMM Keysight 34465A via LAN interface and SCPI commands using PyVisa and PyVISA-py
"""
import pyvisa
import time, sys

class PyVisa_Keysight_34465A():
    def __init__(self, tcp_ip):
        self._ip = tcp_ip
        self._delay = 0.01 # delay for writing the commands in seconds (10 ms)
        self._measurement_configured = False

        self.temp_configs_dict = {  "00_PT100_2WIRE":   ("RTD",  100),         # PT100,   100 Ohm, 2-wire
                                    "01_PT100_4WIRE":   ("FRTD", 100),         # PT100,   100 Ohm, 4-wire
                                    "02_PT1000_2WIRE":  ("RTD",  1000),        # PT1000, 1000 Ohm, 2-wire
                                    "03_PT1000_4WIRE":  ("FRTD", 1000),        # PT1000, 1000 Ohm, 4-wire
                                    "04_NTC_5K_2WIRE":  ("THER", 5000),        # thermistor (NTC),  5 kOhm, 2-wire
                                    "05_NTC_5K_4WIRE":  ("FTH",  5000),        # thermistor (NTC),  5 kOhm, 4-wire
                                    "06_NTC_10K_2WIRE": ("THER", 10000),       # thermistor (NTC), 10 kOhm, 2-wire
                                    "07_NTC_10K_4WIRE": ("FTH",  10000),       # thermistor (NTC), 10 kOhm, 4-wire
                                    "08_TC_J_INT":      ("TC",   "J",  "INT"), # thermocouple, type J, internal reference temperature
                                    "09_TC_K_INT":      ("TC",   "K",  "INT"), # thermocouple, type K, internal reference temperature
                                    "10_TC_E_INT":      ("TC",   "E",  "INT"), # thermocouple, type E, internal reference temperature
                                    "11_TC_T_INT":      ("TC",   "T",  "INT"), # thermocouple, type T, internal reference temperature
                                    "12_TC_N_INT":      ("TC",   "N",  "INT"), # thermocouple, type N, internal reference temperature
                                    "13_TC_R_INT":      ("TC",   "R",  "INT"), # thermocouple, type R, internal reference temperature
                                    "14_TC_J_FIX":      ("TC",   "J",  "FIX"), # thermocouple, type J, external reference temperature
                                    "15_TC_K_FIX":      ("TC",   "K",  "FIX"), # thermocouple, type K, external reference temperature
                                    "16_TC_E_FIX":      ("TC",   "E",  "FIX"), # thermocouple, type E, external reference temperature
                                    "17_TC_T_FIX":      ("TC",   "T",  "FIX"), # thermocouple, type T, external reference temperature
                                    "18_TC_N_FIX":      ("TC",   "N",  "FIX"), # thermocouple, type N, external reference temperature
                                    "19_TC_R_FIX":      ("TC",   "R",  "FIX")  # thermocouple, type R, external reference temperature
                                    }
        
        self.res_configs_dict = {   "00_2WIRE": "RES", # resistor 2-wire
                                    "01_4WIRE": "FRES" # resistor, 4-wire
                                    }
        
        self.volt_configs_dict = {  "00_AC": "AC", # voltage AC
                                    "01_DC": "DC"  # voltage DC
                                    }
        
        self.curr_configs_dict = {  "00_AC": "AC", # current AC
                                    "01_DC": "DC"  # current DC
                                    }
        
        self.cap_cont_configs_dict = { "00_CAP": "CAP",  # capacitance
                                       "01_CONT": "CONT" # continuity
                                       }
        
        try:
            if self._ip == []:
                self.status = "No IP address provided"
            elif self._ip != []:
                self.rm = pyvisa.ResourceManager('@py')
                self.dmm_res = 'TCPIP0::%s::INSTR' %self._ip
                self.dmm = self.rm.open_resource(self.dmm_res)
            
                self.status = "Connected"
                self.connected_with = 'LAN over %s' %self._ip

            self._measurement_configured = False
                
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
                    
            self._measurement_configured = False
                    
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
    def confTempMeasure(self, measConf_str, ref_temp=20.0):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            return -1

        # check valid measurement type
        if measConf_str not in self.temp_configs_dict:
            self._measurement_configured = False
            raise TypeError("Configuration {} is NOT a valid one".format(measConf_str))

        # reset device
        self.cmd = '*RST'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        # select temperature measurement
        self.cmd = "FUNC 'TEMP'"
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        # use parameters for RTD (PT100, PT1000, 2-wire or 4-wire)
        if (self.temp_configs_dict[measConf_str][0] == 'RTD' 
            or self.temp_configs_dict[measConf_str][0] == 'FRTD'):
            self.cmd = "TEMP:TRAN:TYPE %s" %self.temp_configs_dict[measConf_str][0]
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            
            # configure R_0 for RTD or FRTD
            self.cmd = "TEMP:TRAN:%s:RES %s" %(self.temp_configs_dict[measConf_str][0], self.temp_configs_dict[measConf_str][1])
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
        
        # use parameters for thermocouple
        elif self.temp_configs_dict[measConf_str][0] == 'TC':
            # configure measurement with thermocouple probe and given type (e.g. K, J, R)
            self.cmd = "CONF:TEMP %s,%s" %(self.temp_configs_dict[measConf_str][0], self.temp_configs_dict[measConf_str][1])
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            
            # configure reference junction temperature to internal (INT) or external (FIX)
            self.cmd = "TEMP:TRAN:%s:RJUN:TYPE %s" %(self.temp_configs_dict[measConf_str][0], self.temp_configs_dict[measConf_str][2])
            self.dmm.write(self.cmd)
            time.sleep(self._delay)

            # set reference junction temperature
            if self.temp_configs_dict[measConf_str][2] == 'FIX':
                self.cmd = "TEMP:TRAN:%s:RJUN %s" %(self.temp_configs_dict[measConf_str][0], ref_temp)
                self.dmm.write(self.cmd)
                time.sleep(self._delay)
            
        # use parameters for thermistor (NTC with 5 or 10 kOhm, 2-wire or 4-wire)
        elif (self.temp_configs_dict[measConf_str][0] == 'THER' 
            or self.temp_configs_dict[measConf_str][0] == 'FTH'):
            self.cmd = "CONF:TEMP %s" %self.temp_configs_dict[measConf_str][0]
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            
            # configure R_0 for thermistor probe (NTC with 5 or 10 kOhm)
            self.cmd = "TEMP:TRAN:%s:TYPE %s" %(self.temp_configs_dict[measConf_str][0], self.temp_configs_dict[measConf_str][1])
            self.dmm.write(self.cmd)
            time.sleep(self._delay)

        # select unit °C to be used for all temperature measurements
        self.cmd = 'UNIT:TEMP C'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self._measurement_configured = True

    # define a CONFigure RESistor MEASUREment function
    def confResMeasure(self, measConf_str):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            return -1

        # check valid measurement type
        if measConf_str not in self.res_configs_dict:
            self._measurement_configured = False
            raise TypeError("Configuration {} is NOT a valid one".format(measConf_str))
            
        # reset device
        self.cmd = '*RST'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self.cmd = "CONF:%s AUTO" %self.res_configs_dict[measConf_str]
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self._measurement_configured = True
        
    # define a CONFigure VOLTage MEASUREment function
    def confVoltMeasure(self, measConf_str):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            return -1

        # check valid measurement type
        if measConf_str not in self.volt_configs_dict:
            self._measurement_configured = False
            raise TypeError("Configuration {} is NOT a valid one".format(measConf_str))
            
        # reset device
        self.cmd = '*RST'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self.cmd = "CONF:VOLT:%s AUTO" %self.volt_configs_dict[measConf_str]
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self._measurement_configured = True
        
    # define a CONFigure CURRent MEASUREment function
    def confCurrMeasure(self, measConf_str):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            return -1

        # check valid measurement type
        if measConf_str not in self.curr_configs_dict:
            self._measurement_configured = False
            raise TypeError("Configuration {} is NOT a valid one".format(measConf_str))
            
        # reset device
        self.cmd = '*RST'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self.cmd = "CONF:CURR:%s AUTO" %self.curr_configs_dict[measConf_str]
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self._measurement_configured = True
        
    # define a CONFigure CAPacitancy and CONTinuity MEASUREment function
    def confCapContMeasure(self, measConf_str):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            return -1

        # check valid measurement type
        if measConf_str not in self.cap_cont_configs_dict:
            self._measurement_configured = False
            raise TypeError("Configuration {} is NOT a valid one".format(measConf_str))
            
        # reset device
        self.cmd = '*RST'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self.cmd = "CONF:%s" %self.cap_cont_configs_dict[measConf_str]
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self._measurement_configured = True
        
    # define a GET CONFIG function
    def getConfig(self):
        if (self.status != "Connected"):
            print("Device is not connected")
            return -1
        
        if not self._measurement_configured:
            print("Measurement is not configured")
            return -1
        
        # get current measurement configuration
        self.cmd = 'CONF?'
        self.ret_val = self.dmm.query(self.cmd)
        
        return self.ret_val
        
    # define a GET MEASUREMENT function
    def getMeasurement(self):
        if (self.status != "Connected"):
            print("Device is not connected")
            return -1
        
        if not self._measurement_configured:
            print("Measurement is not configured")
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
