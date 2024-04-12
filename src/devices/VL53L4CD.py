########################################################################################################################
# @project    EPFL-Herb_Sensors
# @file       src\devices\VL53L4CD.py
# @brief      Author:             MBE
#             Institute:          EPFL
#             Laboratory:         LMTS
#             Software version:   v1.00
#             Created on:         20.02.2024
#             Last modifications: 12.04.2024
#
# Copyright 2021/2024 EPFL-LMTS
# All rights reserved.
# NO HELP WILL BE GIVEN IF YOU MODIFY THIS CODE !!!
########################################################################################################################

# python packages
from PyQt6.QtWidgets import *
import numpy as np
from serial import *
import sys
# custom packages
from src.options.DxRecord import DxRecord
from src.plots.DxPlot import DxPlot


########################################################################################################################
class VL53L4CD_Sat_HelloWorld(QWidget):
    def __init__(self, parent=None, settings=None, estimate_rate=None):
        QWidget.__init__(self, parent=parent)

        # ------------------------------------------------------------------------------------------------------------ #
        self.data = None
        self.settings = settings
        self.estimateRate = estimate_rate

        # ------------------------------------------------------------------------------------------------------------ #
        # TEMP. PLOTS
        self.distance_plot = DxPlot(tittle="Distance", y_max=1000)
        self.signal_plot = DxPlot(tittle="Signal", y_max=50000)

        # init data arrays + time basis,...
        self.tplot = np.arange(-20 * self.estimateRate, 0.0, self.estimateRate, dtype=float)
        self.t_save = np.zeros(20, dtype=int)

        # Low Voltage set by user
        self.status = np.zeros(20, dtype=float)
        self.status_now = []

        # Low Voltage monitor
        self.distance = np.zeros(20, dtype=float)
        self.distance_now = []

        # High Voltage error
        self.signal = np.zeros(20, dtype=float)
        self.signal_now = []

        # ------------------------------------------------------------------------------------------------------------ #
        # SERIAL COMMUNICATION
        # open serial port
        try:
            self.ser = Serial(self.settings['com_port'], 115200, timeout=0.5)
        except Exception as err_com_port:
            print("[ERR.] Please make sure than you use the right COM port: {}".format(err_com_port))
            sys.exit(-1)
        # ------------------------------------------------------------------------------------------------------------ #
        # remove old data in input buffer
        self.ser.reset_input_buffer()

        # ------------------------------------------------------------------------------------------------------------ #
        # Read a first time to ensure connection (?)
        line = self.ser.readline()
        line.decode("utf-8")

        # read from serial
        try:
            line = self.ser.readline()
            line.decode("utf-8")
        except Exception as e:
            print("[ERR] unable to read line: {}".format(e))
            self.try_reconnect()
            return

        # ------------------------------------------------------------------------------------------------------------ #
        # init file to record data
        if self.settings['record']:
            self.RecordData = DxRecord(parameters=self.settings)

    # **************************************************************************************************************** #
    # INITIALIZE HXL PS VI
    def init_vi(self):
        """
        Initialise VI
        """
        layout_main = QVBoxLayout()
        layout_main.setSpacing(3)
        layout_main.addWidget(self.distance_plot)
        layout_main.addWidget(self.signal_plot)
        # Data save info
        if self.settings['record']:
            layout_main.addWidget(self.RecordData)

        layout_main.addStretch(1)

        self.setLayout(layout_main)

    # **************************************************************************************************************** #
    # CALLBACK
    def data_reader_callback(self):
        """
        callback function
        """
        # ------------------------------------------------------------------------------------------------------------ #
        # shift data in the array one sample left
        self.tplot[:-1] = self.tplot[1:]
        self.tplot[-1] = self.tplot[-2] + self.estimateRate
        # ------------------------------------------------------------------------------------------------------------ #
        self.status[:-1] = self.status[1:]
        self.distance[:-1] = self.distance[1:]
        self.signal[:-1] = self.signal[1:]
        # ------------------------------------------------------------------------------------------------------------ #
        # read from serial
        try:
            line = self.ser.readline()
            line = line.decode("utf-8")
            line = line.replace("\n", "")
            if (self.settings['debug']) and (line != "\r"):
                print("[DBG] {}".format(line))
        except Exception as e:
            print("[ERR] unable to read line: {}".format(e))
            self.try_reconnect()
            return

        # ------------------------------------------------------------------------------------------------------------ #
        # handle data
        # Remove units, spaces, split with coma
        # Refer to documentation of HVPS to assign data to fields
        self.data = (line.replace("Status = ", "").
                     replace("Distance = ", "").replace(" mm", "").
                     replace("Signal = ", "").replace(" kcps/spad", "").
                     replace("\t", "").replace("\r\n", "").split(","))

        try:
            self.status[-1] = int(self.data[0])
            self.status_now = format(int(self.data[0]))

            if int(self.data[0]) != 0:
                self.distance[-1] = 0
                self.distance_now = 0
            else:
                self.distance[-1] = int(self.data[1])
                self.distance_now = format(int(self.data[1]))

            self.signal[-1] = int(self.data[2])
            self.signal_now = format(int(self.data[2]))

        except Exception as e:
            print("[ERR] Unable to convert line: {} - {}".format(line, e))

        # ------------------------------------------------------------------------------------------------------------ #
        # UPDATE PLOTS/LABELS
        self.distance_plot.update_plot(t=self.tplot, y=self.distance)
        self.distance_plot.update_label(label=self.distance_now)

        self.signal_plot.update_plot(t=self.tplot, y=self.signal)
        self.signal_plot.update_label(label=self.signal_now)

        # ------------------------------------------------------------------------------------------------------------ #
        # save data to file
        if self.settings['record']:
            self.RecordData.save_data(status=self.status[-1], distance=self.distance[-1], signal=self.signal[-1])
        # ************************************************************************************************************ #
        # flush input if too much data not handled: avoid keeping very old values
        if self.ser.in_waiting > 200:
            # print(self.ser.in_waiting)
            self.ser.reset_input_buffer()

    # **************************************************************************************************************** #
    # RECONNECTION WITH BOARD
    def try_reconnect(self):
        """
        Reconnection with board
        """
        self.ser.close()
        try:
            self.ser.open()
            self.ser.reset_input_buffer()
            print("[INFO] reconnected to the board")
        except Exception as err_connection:
            print("[ERR] connection failed: {}".format(err_connection))
            pass

    # **************************************************************************************************************** #
    # RECONNECTION WITH BOARD
    def stop_comm(self):
        """
        Stop communication and recording
        """
        if self.settings['record']:
            self.RecordData.close_record()
