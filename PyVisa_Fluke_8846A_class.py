#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon 13. June CET 2022
@author: Bjoern Kasper (urmel79)
Wrapper class to communicate with the DMM Fluke 8846A via LAN interface and SCPI commands using PyVisa and PyVISA-py
"""
import pyvisa
import time, sys

class PyVisa_Fluke_8846A():
    def __init__(self, tcp_ip, tcp_port):
        self._ip = tcp_ip
        self._port = tcp_port
        self._delay = 0.05 # delay for writing the commands in seconds (50 ms)
        self._measurement_configuration = ''
        self._measurement_configured = False
        
        self.conf_measurement_dict = {  "00_RES":           'CONF:RES DEF',                     # resistor 2-wire
                                        "01_FRES":          'CONF:FRES DEF',                    # resistor 4-wire
                                        "02_RTD":           'CONF:TEMP:RTD',                    # PT100, 2-wire,
                                        "03_FRTD":          'CONF:TEMP:FRTD',                   # PT100, 4-wire,
                                        "04_RTD_RES":       'FUNC1 "TEMP:RTD"; FUNC2 "RES"',    # PT100, 2-wire, resistor 2-wire (secondary display)
                                        "05_FRTD_RES":      'FUNC1 "TEMP:FRTD"; FUNC2 "FRES"',  # PT100, 4-wire, resistor 4-wire (secondary display)
                                        "06_VOLT_AC":       'CONF:VOLT:AC DEF',                 # voltage AC
                                        "07_VOLT_AC_FREQ":  'FUNC1 "VOLT:AC"; FUNC2 "FREQ"',    # voltage AC, frequency (secondary display)
                                        "08_VOLT_DC":       'CONF:VOLT:DC DEF',                 # voltage DC
                                        "09_CURR_AC":       'CONF:CURR:AC DEF',                 # current AC
                                        "10_CURR_AC_FREQ":  'FUNC1 "CURR:AC"; FUNC2 "FREQ"',    # current AC, frequency (secondary display)
                                        "11_CURR_DC":       'CONF:CURR:DC DEF',                 # current DC
                                        "12_CONT":          'CONF:CONT',                        # continuity
                                        "13_CAP":           'CONF:CAP DEF'                      # capacitance
                                     }
        
        try:
            if (self._ip == [] or self._port == []):
                self.status = "No IP address or port provided"
            else:
                self.rm = pyvisa.ResourceManager('@py')
                self.dmm_res = 'TCPIP0::%s::%s::SOCKET' % (self._ip, self._port)
                self.dmm = self.rm.open_resource(self.dmm_res)

                # Fluke 8846A expects \n termination of SCPI commands for both directions (read and write)
                # inspired by https://stackoverflow.com/questions/65630897/python-connect-device-using-visa-tcp-socket-connection
                self.dmm.read_termination = '\n'
                self.dmm.write_termination = '\n'
            
                self.status = "Connected"
                self.list_dev_infos = self.getDevInfos()
                self.connected_with = '%s %s over LAN on %s, port %s' %(self.list_dev_infos[0], self.list_dev_infos[1], self._ip, self._port)

            self._measurement_configured = False
            
        except pyvisa.VisaIOError as e:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Something's went wrong while opening %s:%d. Exception is %s" % (self._ip, self._port, e))
    
    # define a OPEN CONNECTION function
    def openConnection(self, tcp_ip, tcp_port):
        try:
            if self.status == "Disconnected":
                if (tcp_ip == [] or tcp_port == []):
                    self.status = "No IP address or port provided"
                else:
                    self.rm = pyvisa.ResourceManager('@py')
                    self.dmm_res = 'TCPIP0::%s::%s::SOCKET' % (self._ip, self._port)
                    self.dmm = self.rm.open_resource(self.dmm_res)

                    # Fluke 8846A expects \n termination of SCPI commands for both directions (read and write)
                    # inspired by https://stackoverflow.com/questions/65630897/python-connect-device-using-visa-tcp-socket-connection
                    self.dmm.read_termination = '\n'
                    self.dmm.write_termination = '\n'

                    self.status = "Connected"
                    self.list_dev_infos = self.getDevInfos()
                    self.connected_with = '%s %s over LAN on %s, port %s' %(self.list_dev_infos[0], self.list_dev_infos[1], self._ip, self._port)
                    
            self._measurement_configured = False
                    
        except pyvisa.VisaIOError as e:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Something's went wrong while opening %s:%d. Exception is %s" % (tcp_ip, tcp_port, e))
    
    # define a CLOSE CONNECTION function
    def closeConnection(self):
        try:
            if self.status == "Connected":
                # self.dmm_sock.close()
                self.rm.close()
                self.status = "Disconnected"
                self.connected_with = "Nothing"
                
        except pyvisa.VisaIOError as e:
            self.status = "Error"
            print("Something's went wrong while closing %s:%d. Exception is %s" % (self._ip, self._port, e))
            
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
        
    # define a CONFigure MEASUREMENT function
    def confMeasurement(self, measConf_str):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            return -1

        self._measurement_configuration = measConf_str
        
        # check valid measurement type
        if self._measurement_configuration not in self.conf_measurement_dict:
            self._measurement_configured = False
            raise TypeError("Configuration {} is NOT a valid one".format(self._measurement_configuration))
            
        # reset device
        self.cmd = '*RST'
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        # get device into remote mode
        self.cmd = "SYST:REM"
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self.cmd = "%s" %self.conf_measurement_dict[self._measurement_configuration]
        self.dmm.write(self.cmd)
        time.sleep(self._delay)
        
        self._measurement_configured = True
        
        self._dict_dmm_measurement = {}

        if ((self._measurement_configuration == '00_RES') or
            (self._measurement_configuration == '01_FRES')):
                
            self._dict_dmm_measurement['resistance_value'] = 0
            self._dict_dmm_measurement['resistance_unit'] = 'Ohm'
        
        elif ((self._measurement_configuration == '02_RTD') or
            (self._measurement_configuration == '03_FRTD')):

            self._dict_dmm_measurement['temperature_value'] = 0
            self._dict_dmm_measurement['temperature_unit'] = '°C'

        elif ((self._measurement_configuration == '04_RTD_RES') or
            (self._measurement_configuration == '05_FRTD_RES')):
                
            self._dict_dmm_measurement['temperature_value'] = 0
            self._dict_dmm_measurement['temperature_unit'] = '°C'
            self._dict_dmm_measurement['resistance_value'] = 0
            self._dict_dmm_measurement['resistance_unit'] = 'Ohm'
        
        elif (self._measurement_configuration == '06_VOLT_AC'):

            self._dict_dmm_measurement['voltage_value'] = 0
            self._dict_dmm_measurement['voltage_unit'] = 'V AC'

        elif self._measurement_configuration == '07_VOLT_AC_FREQ':
            
            self._dict_dmm_measurement['voltage_value'] = 0
            self._dict_dmm_measurement['voltage_unit'] = 'V AC'
            self._dict_dmm_measurement['frequency_value'] = 0
            self._dict_dmm_measurement['frequency_unit'] = 'Hz'
        
        elif self._measurement_configuration == '08_VOLT_DC':
            
            self._dict_dmm_measurement['voltage_value'] = 0
            self._dict_dmm_measurement['voltage_unit'] = 'V DC'

        elif (self._measurement_configuration == '09_CURR_AC'):

            self._dict_dmm_measurement['current_value'] = 0
            self._dict_dmm_measurement['current_unit'] = 'A AC'
        
        elif self._measurement_configuration == '10_CURR_AC_FREQ':
            
            self._dict_dmm_measurement['current_value'] = 0
            self._dict_dmm_measurement['current_unit'] = 'A AC'
            self._dict_dmm_measurement['frequency_value'] = 0
            self._dict_dmm_measurement['frequency_unit'] = 'Hz'
        
        elif self._measurement_configuration == '11_CURR_DC':
            
            self._dict_dmm_measurement['current_value'] = 0
            self._dict_dmm_measurement['current_unit'] = 'A DC'
        
        elif self._measurement_configuration == '12_CONT':
            
            self._dict_dmm_measurement['continuity_value'] = 0
            self._dict_dmm_measurement['continuity_unit'] = 'Ohm'
        
        elif self._measurement_configuration == '13_CAP':
            
            self._dict_dmm_measurement['capacitancy_value'] = 0
            self._dict_dmm_measurement['capacitancy_unit'] = 'F'
        
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
        # strip whitespaces and newline characters from string
        self.ret_val = self.ret_val.strip()
        
        return self.ret_val
        
    # define a GET MEASUREMENT function
    def getMeasurement(self):
        if (self.status != "Connected"):
            print("Device is not connected")
            return -1
        
        if not self._measurement_configured:
            print("Measurement is not configured")
            return -1
        
        if ((self._measurement_configuration == '04_RTD_RES') or
            (self._measurement_configuration == '05_FRTD_RES') or
            (self._measurement_configuration == '07_VOLT_AC_FREQ') or
            (self._measurement_configuration == '10_CURR_AC_FREQ')):

            # # wait some time before reading data from primary and secondary display
            self.cmd = 'READ?; FETCH2?'

            self.ret_val = self.dmm.query(self.cmd)
            
            # strip whitespaces and newline characters from string and cast to float
            self.ret_val_list = self.ret_val.strip().split(';')
            # print(self.ret_val_list)

            # cast list elements to float
            for self._idx, self._val in enumerate(self.ret_val_list):
                self.ret_val_list[self._idx] = float(self.ret_val_list[self._idx])
            
            # write value at the primary value key
            self.prim_val_key = list(self._dict_dmm_measurement.keys())[0]
            self._dict_dmm_measurement[self.prim_val_key] = self.ret_val_list[0]

            if ((self._measurement_configuration == '04_RTD_RES') or
                (self._measurement_configuration == '05_FRTD_RES')):

                self._dict_dmm_measurement['resistance_value'] = self.ret_val_list[1]

            elif ((self._measurement_configuration == '07_VOLT_AC_FREQ') or
                (self._measurement_configuration == '10_CURR_AC_FREQ')):

                self._dict_dmm_measurement['frequency_value'] = self.ret_val_list[1]
        
        else:
            # # wait some time before reading data from primary display
            self.cmd = 'READ?'

            self.ret_val = self.dmm.query(self.cmd)
            
            # strip whitespaces and newline characters from string and cast to float
            self.ret_val = self.ret_val.strip()
            self.ret_val = float(self.ret_val)
            
            # write value at the primary value key
            self.prim_val_key = list(self._dict_dmm_measurement.keys())[0]
            self._dict_dmm_measurement[self.prim_val_key] = self.ret_val
        
        return self._dict_dmm_measurement
