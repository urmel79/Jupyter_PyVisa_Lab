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
        self._delay = 0.05 # delay for writing the commands in seconds (50 ms)
        self._sock_timeout = 0.5 # timeout for reading TCP sockets in [s]
        self._measurement_configured = False
        self._secondary_display = None
        
        self.conf_measurement_dict = {  "00_RES":     "CONF:RES DEF",       # resistor 2-wire
                                        "01_FRES":    "CONF:FRES DEF",      # resistor 4-wire
                                        "02_RTD":     'FUNC1 "TEMP:RTD"; FUNC2 "RES"',   # PT100, 2-wire, resistor 2-wire (secondary display)
                                        "03_FRTD":    'FUNC1 "TEMP:FRTD"; FUNC2 "FRES"', # PT100, 4-wire, resistor 4-wire (secondary display)
                                        "04_VOLT_AC": 'FUNC1 "VOLT:AC"; FUNC2 "FREQ"',   # voltage AC, frequency (secondary display)
                                        "05_VOLT_DC": "CONF:VOLT:DC DEF",   # voltage DC
                                        "06_CURR_AC": 'FUNC1 "CURR:AC"; FUNC2 "FREQ"',   # current AC, frequency (secondary display)
                                        "07_CURR_DC": "CONF:CURR:DC DEF",   # current DC
                                        "08_CONT":    "CONF:CONT",          # continuity
                                        "09_CAP":     "CONF:CAP DEF"        # capacitance
                                     }
        
        try:
            if self._ip == [] or self._port == []:
                self.status = "No IP address or port provided"
            else:
                self.dmm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.dmm_sock.connect((self._ip, self._port))
                
                # set timeout on blocking socket operations in [s]
                self.dmm_sock.settimeout(self._sock_timeout)
            
                self.status = "Connected"
                self.list_dev_infos = self.getDevInfos()
                self.connected_with = '%s %s over LAN on %s, port %s' %(self.list_dev_infos[0], self.list_dev_infos[1], self._ip, self._port)

            self._measurement_configured = False
            
        except Exception as e:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Something's went wrong while opening %s:%d. Exception is %s" % (self._ip, self._port, e))
    
    # define an internal CLEAR INPUT BUFFER function
    def _clearInputBuffer(self):
        try:
            # read answer with buffer size of 64 bytes and drop it
            while self.dmm_sock.recv(64):
                #time.sleep(self._delay)
                pass
        except:
            pass
    
    # define a OPEN CONNECTION function
    def openConnection(self, tcp_ip, tcp_port):
        try:
            if self.status == "Disconnected":
                if tcp_ip == [] or tcp_port == []:
                    self.status = "No IP address or port provided"
                else:
                    self.dmm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.dmm_sock.connect((tcp_ip, tcp_port))
                    
                    # set timeout on blocking socket operations in [s]
                    self.dmm_sock.settimeout(self._sock_timeout)

                    self.status = "Connected"
                    self.list_dev_infos = self.getDevInfos()
                    self.connected_with = '%s %s over LAN on %s, port %s' %(self.list_dev_infos[0], self.list_dev_infos[1], self._ip, self._port)
                    
            self._measurement_configured = False
                    
        except Exception as e:
            self.status = "Disconnected"
            self.connected_with = 'Nothing'
            print("Something's went wrong while opening %s:%d. Exception is %s" % (tcp_ip, tcp_port, e))
    
    # define a CLOSE CONNECTION function
    def closeConnection(self):
        try:
            if self.status == "Connected":
                self.dmm_sock.close()
                self.status = "Disconnected"
                self.connected_with = "Nothing"
                
        except Exception as e:
            self.status = "Error"
            print("Something's went wrong while closing %s:%d. Exception is %s" % (self._ip, self._port, e))
            
    # define a GET DEVice INFOrmation function
    def getDevInfos(self):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            return -1
        
        # clear input buffer before reading
        self._clearInputBuffer()
        
        # get current measurement configuration
        self.cmd = '*IDN?\n'
        self.dmm_sock.sendall(self.cmd.encode('utf-8'))
        time.sleep(self._delay)
        
        # read answer with buffer size of 64 bytes
        self.ret_val = self.dmm_sock.recv(64)
        # strip whitespaces and newline characters from string
        self.ret_val = self.ret_val.decode().strip()
        # split string into list
        self.ret_list = self.ret_val.split(',')
        
        return self.ret_list
        
    # define a CONFigure MEASUREMENT function
    def confMeasurement(self, measConf_str):
        if (self.status != "Connected"):
            print("Device is not connected")
            self._measurement_configured = False
            return -1

        # check valid measurement type
        if measConf_str not in self.conf_measurement_dict:
            self._measurement_configured = False
            raise TypeError("Configuration {} is NOT a valid one".format(measConf_str))
            
        # reset device
        self.cmd = '*RST\n'
        self.dmm_sock.sendall(self.cmd.encode('utf-8'))
        time.sleep(self._delay)
        
        # get device into remote mode
        self.cmd = "SYST:REM\n"
        self.dmm_sock.sendall(self.cmd.encode('utf-8'))
        time.sleep(self._delay)
        
        self.cmd = "%s\n" %self.conf_measurement_dict[measConf_str]
        self.dmm_sock.sendall(self.cmd.encode('utf-8'))
        time.sleep(self._delay)
        
        self._measurement_configured = True
        
        self._dict_dmm_measurement = {}
        if (measConf_str == '00_RES') or (measConf_str == '01_FRES'):
            self._dict_dmm_measurement['resistance_value'] = 0
            self._dict_dmm_measurement['resistance_unit'] = 'Ohm'
            self._secondary_display = None # secondary display is NOT used
            # set timeout on blocking socket operations in [s]
            self.dmm_sock.settimeout(self._sock_timeout)
        elif (measConf_str == '02_RTD') or (measConf_str == '03_FRTD'):
            self._dict_dmm_measurement['temperature_value'] = 0
            self._dict_dmm_measurement['temperature_unit'] = '°C'
            self._secondary_display = "TEMP" # secondary display is used
            self._dict_dmm_measurement['resistance_value'] = 0
            self._dict_dmm_measurement['resistance_unit'] = 'Ohm'
            # set timeout on blocking socket operations in [s]
            self.dmm_sock.settimeout(0.8)
        elif measConf_str == '04_VOLT_AC':
            self._dict_dmm_measurement['voltage_value'] = 0
            self._dict_dmm_measurement['voltage_unit'] = 'V AC'
            self._secondary_display = "AC" # secondary display is used
            self._dict_dmm_measurement['frequency_value'] = 0
            self._dict_dmm_measurement['frequency_unit'] = 'Hz'
            # set timeout on blocking socket operations in [s]
            self.dmm_sock.settimeout(1.0)
        elif measConf_str == '05_VOLT_DC':
            self._dict_dmm_measurement['voltage_value'] = 0
            self._dict_dmm_measurement['voltage_unit'] = 'V DC'
            self._secondary_display = None # secondary display is NOT used
            # set timeout on blocking socket operations in [s]
            self.dmm_sock.settimeout(self._sock_timeout)
        elif measConf_str == '06_CURR_AC':
            self._dict_dmm_measurement['current_value'] = 0
            self._dict_dmm_measurement['current_unit'] = 'A AC'
            self._secondary_display = "AC" # secondary display is used
            self._dict_dmm_measurement['frequency_value'] = 0
            self._dict_dmm_measurement['frequency_unit'] = 'Hz'
            # set timeout on blocking socket operations in [s]
            self.dmm_sock.settimeout(0.8)
        elif measConf_str == '07_CURR_DC':
            self._dict_dmm_measurement['current_value'] = 0
            self._dict_dmm_measurement['current_unit'] = 'A DC'
            self._secondary_display = None # secondary display is NOT used
            # set timeout on blocking socket operations in [s]
            self.dmm_sock.settimeout(1.0)
        elif measConf_str == '08_CONT':
            self._dict_dmm_measurement['continuity_value'] = 0
            self._dict_dmm_measurement['continuity_unit'] = 'Ohm'
            self._secondary_display = None # secondary display is NOT used
            # set timeout on blocking socket operations in [s]
            self.dmm_sock.settimeout(self._sock_timeout)
        elif measConf_str == '09_CAP':
            self._dict_dmm_measurement['capacitancy_value'] = 0
            self._dict_dmm_measurement['capacitancy_unit'] = 'F'
            self._secondary_display = None # secondary display is NOT used
            # set timeout on blocking socket operations in [s]
            self.dmm_sock.settimeout(2.0)
        
    # define a GET CONFIG function
    def getConfig(self):
        if (self.status != "Connected"):
            print("Device is not connected")
            return -1
        
        if not self._measurement_configured:
            print("Measurement is not configured")
            return -1
        
        # clear input buffer before reading
        self._clearInputBuffer()
        
        # get current measurement configuration
        self.cmd = 'CONF?\n'
        self.dmm_sock.sendall(self.cmd.encode('utf-8'))
        time.sleep(self._delay)
        
        # read answer with buffer size of 64 bytes
        self.ret_val = self.dmm_sock.recv(64)
        # strip whitespaces and newline characters from string
        self.ret_val = self.ret_val.decode().strip()
        
        return self.ret_val
        
    # define a GET MEASUREMENT function
    def getMeasurement(self):
        if (self.status != "Connected"):
            print("Device is not connected")
            return -1
        
        if not self._measurement_configured:
            print("Measurement is not configured")
            return -1
        
        # clear input buffer before reading
        self._clearInputBuffer()
        
        if (self._secondary_display == "TEMP") or (self._secondary_display == "AC"):
            # wait some time before reading data from primary and secondary display
            time.sleep(self._delay)
            self.cmd = 'READ?; FETCH2?\n'
            self.dmm_sock.sendall(self.cmd.encode('utf-8'))
            time.sleep(self._delay)
            # read answer with buffer size of 64 bytes
            self.ret_val = self.dmm_sock.recv(64)
            
            # strip whitespaces and newline characters from string and cast to float
            self.ret_val_list = self.ret_val.decode().strip().split(';')
            print(self.ret_val_list)
            # cast list elements to float
            for self._idx, self._val in enumerate(self.ret_val_list):
                self.ret_val_list[self._idx] = float(self.ret_val_list[self._idx])
            
            # write value at the primary value key
            self.prim_val_key = list(self._dict_dmm_measurement.keys())[0]
            self._dict_dmm_measurement[self.prim_val_key] = self.ret_val_list[0]

            if self._secondary_display == "TEMP":
                self._dict_dmm_measurement['resistance_value'] = self.ret_val_list[1]
            elif self._secondary_display == "AC":
                self._dict_dmm_measurement['frequency_value'] = self.ret_val_list[1]
        
        elif self._secondary_display == None:
            # wait some time before reading data from primary display
            time.sleep(self._delay)
            self.cmd = 'READ?\n'
            self.dmm_sock.sendall(self.cmd.encode('utf-8'))
            time.sleep(self._delay)
            # read answer with buffer size of 64 bytes
            self.ret_val = self.dmm_sock.recv(64)
            
            # strip whitespaces and newline characters from string and cast to float
            self.ret_val = self.ret_val.decode().strip()
            self.ret_val = float(self.ret_val)
            
            # write value at the primary value key
            self.prim_val_key = list(self._dict_dmm_measurement.keys())[0]
            self._dict_dmm_measurement[self.prim_val_key] = self.ret_val
        
        return self._dict_dmm_measurement
