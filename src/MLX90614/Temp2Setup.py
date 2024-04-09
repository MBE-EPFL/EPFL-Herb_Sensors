########################################################################################################################
# @project    EPFL-Temp_Setup_#2
# @file       Temp2Setup.py
# @brief      Author:             MBE
#             Institute:          EPFL
#             Laboratory:         LMTS
#             Software version:   v1.00
#             Created on:         20.02.2024
#             Last modifications: 20.02.2024
#
# Copyright 2021/2024 EPFL-LMTS
# All rights reserved.
# NO HELP WILL BE GIVEN IF YOU MODIFY THIS CODE !!!
########################################################################################################################

# python packages
import numpy as np
from serial import *
import sys
# custom packages
from src.MLX90614.Temp2Plot import *
from src.MLX90614.Temp2Record import *


class Temp2Setup(QWidget):
    def __init__(self, parent=None, port_name=None, estimate_rate=None, scales=None, debug_mode=None, record_data=None):

        QWidget.__init__(self, parent=parent)
        # ************************************************************************************************************ #
        self.data = None
        self.port_name = port_name
        self.estimateRate = estimate_rate
        self.scale = scales
        self.debug_mode = debug_mode
        self.record_data = record_data
        # ************************************************************************************************************ #
        # TEMP. PLOTS
        self.temp_plot = Temp2Plot(plot_tittle="Temp. Monitor", scale=self.scale)
        # Low Voltage set by user
        self.temp_ambient = np.zeros(20, dtype=float)
        self.temp_ambient_now = []
        # Low Voltage monitor
        self.temp_object = np.zeros(20, dtype=float)
        self.temp_object_now = []
        # High Voltage error
        self.temp_err = np.zeros(20, dtype=float)
        self.temp_err_now = []

        # ************************************************************************************************************ #
        # FOR ANY PLOT (CURRENT OR VOLTAGE)
        # init data arrays + time basis,...
        self.tplot = np.arange(-20 * self.estimateRate, 0.0, self.estimateRate, dtype=float)
        self.t_save = np.zeros(20, dtype=int)

        # ************************************************************************************************************ #
        # SERIAL COMMUNICATION
        # ------------------------------------------------------------------------------------------------------------ #
        # open serial port
        try:
            self.ser = Serial(self.port_name, 9600, timeout=0.5)
        except Exception as err_com_port:
            print("[ERR.] Please make sure than you use the right COM port: {}".format(err_com_port))
            sys.exit(-1)
        # ------------------------------------------------------------------------------------------------------------ #
        # remove old data in input buffer
        self.ser.reset_input_buffer()

        # ************************************************************************************************************ #
        # Read a first time to ensure connection (?)
        line = self.ser.readline()
        line = line.decode("utf-8")

        # read from serial
        try:
            line = self.ser.readline()
            line = line.decode("utf-8")
        except Exception as e:
            print("[ERR] unable to read line: {}".format(e))
            self.try_reconnect()
            return

        # ************************************************************************************************************ #
        # handle data
        # Remove units, spaces, split with coma
        # Refer to documentation of HVPS to assign data to fields

        self.rcv_data_label = QLabel("Received data: ND")
        self.data_recv_layout = QVBoxLayout()
        self.data_recv_layout.addWidget(self.rcv_data_label)

        # ************************************************************************************************************ #
        # init file to record data
        if self.record_data == 1:
            self.RecordData = Temp2Record(port_name=port_name)

    ####################################################################################################################
    # INITIALIZE HXL PS VI
    def init_vi(self):
        layout_main = QVBoxLayout()
        self.setLayout(layout_main)
        layout_main.setSpacing(3)
        # ************************************************************************************************************ #
        # add top layout to main layout
        layout_main.addWidget(self.temp_plot)

        # ************************************************************************************************************ #
        # Layout of all widgets not plot
        layout_main.addStretch(1)

    ####################################################################################################################
    # CALLBACK
    def data_reader_callback(self):
        # ************************************************************************************************************ #
        # shift data in the array one sample left
        self.tplot[:-1] = self.tplot[1:]
        self.tplot[-1] = self.tplot[-2] + self.estimateRate
        # ------------------------------------------------------------------------------------------------------------ #
        self.temp_ambient[:-1] = self.temp_ambient[1:]
        self.temp_object[:-1] = self.temp_object[1:]
        self.temp_err[:-1] = self.temp_err[1:]
        # ************************************************************************************************************ #
        # read from serial
        try:
            line = self.ser.readline()
            line = line.decode("utf-8")
            line = line.replace("\n", "")
            if (self.debug_mode == 1) and (line != "\r"):
                print("[DBG] {}".format(line))
        except Exception as e:
            print("[ERR] unable to read line: {}".format(e))
            self.try_reconnect()
            return

        # ************************************************************************************************************ #
        # handle data
        # Remove units, spaces, split with coma
        # Refer to documentation of HVPS to assign data to fields
        if (self.scale == 'Celsius') and ('C' in line):
            self.data = (line.replace("Ambient = ", "").replace("Object = ", "").
                         replace("*C", "").replace("\r\n", "").split("\t"))
        elif (self.scale == 'Fahrenheit') and ('F' in line):
            self.data = (line.replace("Ambient = ", "").replace("Object = ", "").
                         replace("*F", "").replace("\r\n", "").split("\t"))

        try:
            self.temp_ambient[-1] = float(self.data[0])
            self.temp_ambient_now = format(float(self.data[0]), '2.2f')

            self.temp_object[-1] = float(self.data[1])
            self.temp_object_now = format(float(self.data[1]), '2.2f')

            self.temp_err[-1] = float(self.data[1]) - float(self.data[0])
            self.temp_err_now = format((float(self.data[1]) - float(self.data[0])), '2.2f')

        except Exception as e:
            print("[ERR] Unable to convert line: {} - {}".format(line, e))

        # ************************************************************************************************************ #
        # UPDATE PLOTS/LABELS
        self.temp_plot.update_plot(t=self.tplot, y1=self.temp_ambient, y2=self.temp_object)
        self.temp_plot.update_label(label1=self.temp_ambient_now, label2=self.temp_object_now, label3=self.temp_err_now)

        # ************************************************************************************************************ #
        # save data to file
        if self.record_data == 1:
            self.RecordData.save_data(t_ambient=self.temp_ambient[-1],
                                      t_object=self.temp_object[-1],
                                      t_error=self.temp_err[-1])
        # ************************************************************************************************************ #
        # flush input if too much data not handled: avoid keeping very old values
        if self.ser.in_waiting > 200:
            # print(self.ser.in_waiting)
            self.ser.reset_input_buffer()

    ####################################################################################################################
    # RECONNECTION WITH BOARD
    def try_reconnect(self):
        self.ser.close()
        try:
            self.ser.open()
            self.ser.reset_input_buffer()
            print("[INFO] reconnected to the board")
        except Exception as err_connection:
            print("[ERR] connection failed: {}".format(err_connection))
            pass

    ####################################################################################################################
    # RECONNECTION WITH BOARD
    def stop_comm(self):
        if self.record_data == 1:
            self.record_data = 0
            self.RecordData.close_record()
