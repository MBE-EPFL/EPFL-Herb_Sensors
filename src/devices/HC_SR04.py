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
from src.options.Dx2Record import Dx2Record
from src.plots.Dx2Plot import Dx2Plot


########################################################################################################################
class HC_SR04_Simple(QWidget):
    def __init__(self, parent=None, settings=None, estimate_rate=None):
        QWidget.__init__(self, parent=parent)

        # ------------------------------------------------------------------------------------------------------------ #
        self.data = None
        self.settings = settings
        self.estimateRate = estimate_rate

        # ------------------------------------------------------------------------------------------------------------ #
        # TEMP. PLOTS
        self.distance_plot = Dx2Plot(tittle="Distance", y_max=40)
        # init data arrays + time basis,...
        self.tplot = np.arange(-40 * self.estimateRate, 0.0, self.estimateRate, dtype=float)
        self.t_save = np.zeros(40, dtype=int)

        self.distance = np.zeros(40, dtype=float)
        self.distance_now = []

        # ------------------------------------------------------------------------------------------------------------ #
        # SERIAL COMMUNICATION
        # open serial port
        try:
            self.ser = Serial(self.settings['com_port'], 9600, timeout=0.5)
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

        # ------------------------------------------------------------------------------------------------------------ #
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
            self.RecordData = Dx2Record(port_name=self.settings['com_port'])

    # **************************************************************************************************************** #
    def init_vi(self):
        """
        Initialise VI
        """
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.distance_plot)
        if self.settings['record']:
            layout_main.addWidget(self.RecordData)

        layout_main.setSpacing(3)
        layout_main.addStretch(1)
        self.setLayout(layout_main)

    # **************************************************************************************************************** #
    def data_reader_callback(self):
        """
        callback function
        """
        # ------------------------------------------------------------------------------------------------------------ #
        # shift data in the array one sample left
        self.tplot[:-1] = self.tplot[1:]
        self.tplot[-1] = self.tplot[-2] + self.estimateRate
        self.distance[:-1] = self.distance[1:]

        # ------------------------------------------------------------------------------------------------------------ #
        # read from serial
        while 1:
            try:
                line = self.ser.readline()
            except Exception as err_reading:
                self.try_reconnect()
                line = b""
                print(f"[ERR] reading failed: {err_reading}")

            new_line = line.decode("utf-8")

            if new_line.startswith("1:"):
                break

        try:
            new_line = new_line.replace("\n", "")
            if (self.settings['debug']) and (new_line != "\r"):
                print("[DBG] {}".format(new_line))
        except Exception as e:
            print("[ERR] unable to read line: {}".format(e))
            self.try_reconnect()
            return

        # ------------------------------------------------------------------------------------------------------------ #
        # handle data
        # Remove units, spaces, split with coma
        # Refer to documentation of HVPS to assign data to fields
        self.data = (new_line.replace("1: ", "").replace(" cm", "")
                     .replace("\t", "").replace("\r\n", ""))

        try:
            self.distance[-1] = float(self.data)
            self.distance_now = format(float(self.data))
        except Exception as e:
            print("[ERR] Unable to convert line: {} - {}".format(new_line, e))

        # ------------------------------------------------------------------------------------------------------------ #
        # UPDATE PLOTS/LABELS
        self.distance_plot.update_plot(t=self.tplot, y=self.distance)
        self.distance_plot.update_label(label=self.distance_now)

        # ------------------------------------------------------------------------------------------------------------ #
        # save data to file
        if self.settings['record']:
            self.RecordData.save_data(distance=self.distance[-1])

        # ------------------------------------------------------------------------------------------------------------ #
        # flush input if too much data not handled: avoid keeping very old values
        if self.ser.in_waiting > 200:
            # print(self.ser.in_waiting)
            self.ser.reset_input_buffer()

    # **************************************************************************************************************** #
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
    def stop_comm(self):
        """
        Stop communication and recording
        """
        if self.settings['record']:
            self.RecordData.close_record()
