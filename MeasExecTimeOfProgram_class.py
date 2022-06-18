#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat 18. June CET 2022
@author: Bjoern Kasper (urmel79)
Class to measure execution time of a program
"""
import time
import pandas as pd

class MeasExecTimeOfProgram():
    def __init__(self):
        self._startTime = 0
        self._stopTime = 0
        self._deltaTime = 0
        
        self._header = ["Time samples [ms]"]
        self._df_log_buffer = pd.DataFrame(columns=self._header)

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
    
    # define a START function
    def start(self):
        self._startTime = time.time()
        return 0

    # define a STOP function
    def stop(self):
        self._stopTime = time.time()

        self._deltaTime = self._stopTime - self._startTime

        # return execution time in milliseconds
        return self._deltaTime*1000
    
    # define a INIT LOGGER function
    def initLogger(self):
        self._df_log_buffer = pd.DataFrame(columns=self._header)
        return 0
    
    # define a ADD SAMPLE function
    def addSample(self, deltaTime):
        # log incoming rows to buffer (dataframe)
        self._dataframe_add_row(self._df_log_buffer, deltaTime)
        return 0
        
    # define a GET LOG BUFFER function
    def getLogBuffer(self):
        return self._df_log_buffer
    
    # define a GET STATISTICS
    def getStatistics(self):
        # FIRST: make a deep copy for doing statistics
        self._df_log_buffer_copy = self._df_log_buffer.copy(deep=True)
        
        # drop first row of dataframe to kill outlier
        self._df_log_buffer_copy.drop(index=self._df_log_buffer_copy.head(1).index, inplace=True)
        # reset index of dataframe
        self._df_log_buffer_copy.reset_index(inplace=True, drop=True)

        return self._df_log_buffer_copy['Time samples [ms]'].describe()
