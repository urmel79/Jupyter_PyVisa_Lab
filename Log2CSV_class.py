#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fr 25. Mar CET 2022
@author: Bjoern Kasper (urmel79)
Class for logging dataframes holding e.g. measuring data to a CSV file.

To avoid premature wear of flash memory (e.g. microSD cards) by permanent writing of files, 
the incoming data is first collected in an internal buffer dataframe and only written to 
the CSV file after a predefined time interval.
"""

import pandas as pd
import time

class Log2CSV():
    def __init__(self, str_csv_file, int_log_intervall_sec, list_header):
        self._csv_file = str_csv_file
        self._log_intervall = int_log_intervall_sec
        self._header = list_header
        
        self._row = []
        
        self._df_log_buffer = pd.DataFrame(columns=self._header)
        
        # create csv file and write header
        self._write_csv_header()
        
        self._time_last_write = time.time()
    
    # internal function to add rows to dataframe
    def _dataframe_add_row(self, df=None, row=[]):
        if (df is None):
            return

        # add a row
        df.loc[-1] = row

        # shift the index
        df.index = df.index + 1

        # reset the index of dataframe and avoid the old index being added as a column
        df.reset_index(drop=True, inplace=True)
    
    # internal function to write the csv header
    def _write_csv_header(self):
        try:
            # write buffer to csv file in write mode (new file will be created)
            self._df_log_buffer.to_csv(self._csv_file, sep ='\t', index = False, header=True, mode='w')
        except Exception as ex:
            print('Writing to CSV file raised the error: "{}"'.format(ex))
    
    # external function to log data to buffer (dataframe)
    # and write to csv file from time to time
    def log_data(self, list_row):
        # log incoming rows to buffer (dataframe)
        self._dataframe_add_row(self._df_log_buffer, list_row)
        
        self._time_now = time.time()
        self._time_delta = self._time_now - self._time_last_write
        if (self._time_delta >= self._log_intervall):
            try:
                # write buffer to csv file in append mode (data will added to existing file)
                self._df_log_buffer.to_csv(self._csv_file, sep ='\t', index = False, header=False, mode='a')
            except Exception as ex:
                print('Writing to CSV file raised the error: "{}"'.format(ex))
            
            # reset (re-initialize) buffer
            self._df_log_buffer = pd.DataFrame(columns=self._header)
            
            # save time of last write
            self._time_last_write = self._time_now
