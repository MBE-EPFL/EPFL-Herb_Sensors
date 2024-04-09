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
from PyQt6.QtCore import *
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from serial import *
import sys
from PyQt6.QtWidgets import *
# custom packages
# from src.MLX90614.Temp1Plot import *
# from src.MLX90614.Temp1Record import *


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, t_min=None, t_max=None):
        #####################################
        # Start and Format Figure
        #####################################
        plt.rcParams.update({'font.size': 16})
        fig_dims = (12, 9)  # figure size
        self.fig, self. ax = plt.subplots(figsize=fig_dims)  # start figure
        pix_res = (8, 8)  # pixel resolution
        zz = np.zeros(pix_res)  # set array with zeros first
        self.im1 = self.ax.imshow(zz, vmin=t_min, vmax=t_max)  # plot image, with temperature bounds
        cbar = self.fig.colorbar(self.im1, fraction=0.0475, pad=0.03)  # colorbar
        cbar.set_label('Temperature [C]', labelpad=10)  # temp. label

        super(MplCanvas, self).__init__(self.fig)

    def update_data(self, new_data):
        self.im1.set_data(new_data)
        self.fig.canvas.draw_idle()


class Temp1Setup(QWidget):
    def __init__(self, parent=None, port_name=None, debug_mode=None, t_min=None, t_max=None):

        QWidget.__init__(self, parent=parent)
        # ************************************************************************************************************ #
        self.data = None
        self.port_name = port_name
        self.debug_mode = debug_mode
        self.cnt_line = 0
        self.data_tab = []
        self.total_data = None
        self.total_data_float = None

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
        # line = line.decode("utf-8")

        # read from serial
        try:
            line = self.ser.readline()
            # line = line.decode("utf-8")
        except Exception as e:
            print("[ERR] unable to read line: {}".format(e))
            self.try_reconnect()
            return

        # ************************************************************************************************************ #
        # handle data
        # Remove units, spaces, split with coma
        # Refer to documentation of HVPS to assign data to fields

        self.canvas = MplCanvas(t_min=t_min, t_max=t_max)

    ####################################################################################################################
    # INITIALIZE HXL PS VI
    def init_vi(self):
        layout_main = QHBoxLayout()
        layout_main.setSpacing(0)
        self.setLayout(layout_main)
        # ************************************************************************************************************ #
        # add canvas to main layout
        layout_main.addWidget(self.canvas)
        layout_main.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # ************************************************************************************************************ #
        # Layout of all widgets not plot
        layout_main.addStretch(1)

    ####################################################################################################################
    # CALLBACK
    def data_reader_callback(self):
        # ************************************************************************************************************ #
        # read from serial
        try:
            line = self.ser.readline()
            line = line.decode("utf-8")
            line = line.replace("\n", "")
        except Exception as e:
            print("[ERR] unable to read line: {}".format(e))
            self.try_reconnect()
            return

        # -------------------------------------------------------------------------------------------------------- #
        if line.startswith("AMG88xx") or line.startswith("--") or line.startswith("]") or line == "\r":
            return
        else:
            # if (self.debug_mode == 1) and (line != "]"):
                # print("[DBG] {}".format(line))
            # ************************************************************************************************ #
            # handle data
            # Remove units, spaces, split with coma
            # Refer to documentation of HVPS to assign data to fields
            if self.cnt_line == 0:
                self.data_tab = []
                self.total_data = None
                self.total_data_float = None
                self.data = (line.replace("[", "").replace("\n", "").split(", "))
                self.data.remove('\r')
                self.total_data = self.data
                self.cnt_line += 1
            elif 0 < self.cnt_line < 7:
                self.data = (line.replace("[", "").replace("\n", "").split(", "))
                self.data.remove('\r')
                self.total_data += self.data
                self.cnt_line += 1
            else:
                self.cnt_line = 0
                self.data = (line.replace("[", "").replace("\r", "").replace("\n", "").split(", "))
                self.data.remove('')
                self.total_data += self.data

                print("[TAB] {}".format(self.total_data))

                # ************************************************************************************************ #
                # UPDATE FIGURE
                # Convertir en une matrice 8x8
                new_data_matrix = np.array(self.total_data, dtype=float).reshape(8, 8)

                self.canvas.update_data(new_data_matrix)

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
