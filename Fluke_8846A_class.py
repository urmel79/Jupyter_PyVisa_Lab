#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat 04. June CET 2022
@author: Bjoern Kasper (urmel79)
Wrapper class to communicate with the DMM Fluke 8846A via LAN interface and SCPI commands using TCP sockets
"""
import socket
import time, sys

class Fluke_8846A():
    def __init__(self, tcp_ip, tcp_port):
        self._ip = tcp_ip
        self._port = tcp_port
        self._delay = 0.01 # delay for writing the commands in seconds (10 ms)
        self._measurement_configured = False
        self._measType = "DC"
        
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
            if self._ip == [] or self._port == []:
                self.status = "No IP address or port provided"
            else:
                #self.rm = pyvisa.ResourceManager('@py')
                #self.dmm_res = 'TCPIP0::%s::3490::SOCKET' %self._ip
                #self.dmm = self.rm.open_resource(self.dmm_res)
                
                self.dmm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.dmm_sock.connect((self._ip, self._port))
            
                self.status = "Connected"
                #self.list_dev_infos = self.getDevInfos()
                #self.connected_with = '%s %s over LAN on %s' %(self.list_dev_infos[0], self.list_dev_infos[1], self._ip)

            self._measurement_configured = False
            self._measType = "DC"
            
        except Exception as e:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Something's wrong with %s:%d. Exception is %s" % (self._ip, self._port, e))
    
        #except pyvisa.VisaIOError:
        #    self.status = "Disconnected"
        #    self.connected_with = 'Nothing'
        #    print("Pyvisa is not able to connect with the device")
    
    # define a OPEN CONNECTION function
    def openConnection(self, tcp_ip, tcp_port):
        try:
            if self.status == "Disconnected":
                if tcp_ip == [] or tcp_port == []:
                    self.status = "No IP address or port provided"
                else:
                    #self.rm = pyvisa.ResourceManager('@py')
                    #self.dmm_res = 'TCPIP0::%s::INSTR' %tcp_ip
                    #self.dmm = self.rm.open_resource(self.dmm_res)
                    
                    self.dmm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.dmm_sock.connect((tcp_ip, tcp_port))

                    self.status = "Connected"
                    #self.list_dev_infos = self.getDevInfos()
                    #self.connected_with = '%s %s over LAN on %s' %(self.list_dev_infos[0], self.list_dev_infos[1], self._ip)
                    
            self._measurement_configured = False
            self._measType = "DC"
                    
        except Exception as e:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Something's wrong with %s:%d. Exception is %s" % (tcp_ip, tcp_port, e))
    
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
            
    # define a GET DEVice INFOrmation function
    def getDevInfos(self):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            return -1
        
        # get current measurement configuration
        self.cmd = '*IDN?'
        self.ret_val = self.dmm.query(self.cmd)
        # strip whitespaces and newline characters from string
        self.ret_val = self.ret_val.strip()
        # split string into list
        self.ret_list = self.ret_val.split(',')
        
        return self.ret_list
    
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
        
        self._dict_dmm_measurement = {}
        self._dict_dmm_measurement['temperature_value'] = 0
        self._dict_dmm_measurement['temperature_unit'] = '°C'

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
        
        self._dict_dmm_measurement = {}
        self._dict_dmm_measurement['resistance_value'] = 0
        self._dict_dmm_measurement['resistance_unit'] = 'Ohm'
        
    # define a CONFigure VOLTage MEASUREment function
    def confVoltMeasure(self, measConf_str):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            self._measType = "DC"
            return -1

        # check valid measurement type
        if measConf_str not in self.volt_configs_dict:
            self._measurement_configured = False
            self._measType = "DC"
            raise TypeError("Configuration {} is NOT a valid one".format(measConf_str))
            
        # reset device
        self.cmd = '*RST'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self.cmd = "CONF:VOLT:%s AUTO" %self.volt_configs_dict[measConf_str]
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        if measConf_str == "00_AC":
            self.cmd = "VOLT:AC:SEC 'FREQ'"
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            self._measType = "AC"
        
        self._measurement_configured = True
        
        self._dict_dmm_measurement = {}
        self._dict_dmm_measurement['voltage_value'] = 0
        self._dict_dmm_measurement['voltage_unit'] = 'V DC'
        
        if self._measType == "AC":
            self._dict_dmm_measurement['voltage_unit'] = 'V AC'
            self._dict_dmm_measurement['frequency_value'] = 0
            self._dict_dmm_measurement['frequency_unit'] = 'Hz'
        
    # define a CONFigure CURRent MEASUREment function
    def confCurrMeasure(self, measConf_str):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            self._measType = "DC"
            return -1

        # check valid measurement type
        if measConf_str not in self.curr_configs_dict:
            self._measurement_configured = False
            self._measType = "DC"
            raise TypeError("Configuration {} is NOT a valid one".format(measConf_str))
            
        # reset device
        self.cmd = '*RST'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self.cmd = "CONF:CURR:%s AUTO" %self.curr_configs_dict[measConf_str]
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        if measConf_str == "00_AC":
            self.cmd = "CURR:AC:SEC 'FREQ'"
            self.dmm.write(self.cmd)
            time.sleep(self._delay)
            self._measType = "AC"
        
        self._measurement_configured = True
        
        self._dict_dmm_measurement = {}
        self._dict_dmm_measurement['current_value'] = 0
        self._dict_dmm_measurement['current_unit'] = 'A DC'
        
        if self._measType == "AC":
            self._dict_dmm_measurement['current_unit'] = 'A AC'
            self._dict_dmm_measurement['frequency_value'] = 0
            self._dict_dmm_measurement['frequency_unit'] = 'Hz'
        
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
        
        self._dict_dmm_measurement = {}
        if measConf_str == '00_CAP':
            self._dict_dmm_measurement['capacitancy_value'] = 0
            self._dict_dmm_measurement['capacitancy_unit'] = 'F'
        elif measConf_str == '01_CONT':
            self._dict_dmm_measurement['continuity_value'] = 0
            self._dict_dmm_measurement['continuity_unit'] = 'Ohm'
        
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
        #time.sleep(self._delay)
        
        # write value at the primary value key
        self.prim_val_key = list(self._dict_dmm_measurement.keys())[0]
        self._dict_dmm_measurement[self.prim_val_key] = self.ret_val
        
        if self._measType == "AC":
            # retrieve data from secondary display
            self.cmd = 'DATA2?'
            # wait some time before reading data from secondary display
            time.sleep(0.15)
            self.ret_val = self.dmm.query(self.cmd)
            self.ret_val = float(self.ret_val)
            time.sleep(self._delay)
            self._dict_dmm_measurement['frequency_value'] = self.ret_val

        return self._dict_dmm_measurement
