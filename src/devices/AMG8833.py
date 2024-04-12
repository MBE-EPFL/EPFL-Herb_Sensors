########################################################################################################################
# @project    EPFL-Herb_Sensors
# @file       src\devices\AMG8833.py
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
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from serial import *
import sys


########################################################################################################################
class MplCanvas(FigureCanvas):
    def __init__(self, t_min=None, t_max=None):
        # ------------------------------------------------------------------------------------------------------------ #
        # Start and Format Figure
        plt.rcParams.update({'font.size': 16})
        fig_dims = (12, 9)  # figure size
        self.fig, self. ax = plt.subplots(figsize=fig_dims)  # start figure
        pix_res = (8, 8)  # pixel resolution
        zz = np.zeros(pix_res)  # set array with zeros first
        self.im1 = self.ax.imshow(zz, vmin=t_min, vmax=t_max)  # plot image, with temperature bounds
        cbar = self.fig.colorbar(self.im1, fraction=0.0475, pad=0.03)  # colorbar
        cbar.set_label('Temperature [C]', labelpad=10)  # temp. label

        super(MplCanvas, self).__init__(self.fig)

    # **************************************************************************************************************** #
    def update_data(self, new_data):
        self.im1.set_data(new_data)
        self.fig.canvas.draw_idle()


########################################################################################################################
class pixel_test(QWidget):
    def __init__(self, parent=None, settings=None):
        QWidget.__init__(self, parent=parent)

        # ------------------------------------------------------------------------------------------------------------ #
        self.data = None
        self.parameters = settings
        self.cnt_line = 0
        self.data_tab = []
        self.total_data = None
        self.total_data_float = None

        # ------------------------------------------------------------------------------------------------------------ #
        # SERIAL COMMUNICATION
        # open serial port
        try:
            self.ser = Serial(self.parameters['com_port'], 9600, timeout=0.5)
        except Exception as err_com_port:
            print("[ERR.] Please make sure than you use the right COM port: {}".format(err_com_port))
            sys.exit(-1)

        # ------------------------------------------------------------------------------------------------------------ #
        # remove old data in input buffer
        self.ser.reset_input_buffer()

        # ------------------------------------------------------------------------------------------------------------ #
        # Read a first time to ensure connection (?)
        self.ser.readline()

        # ------------------------------------------------------------------------------------------------------------ #
        # read from serial
        try:
            self.ser.readline()
        except Exception as e:
            print("[ERR] unable to read line: {}".format(e))
            self.try_reconnect()
            return

        self.canvas = MplCanvas(t_min=self.parameters['t_min'], t_max=self.parameters['t_max'])

    # ****************************************************************************************************************
    def init_vi(self):
        """
        Initialise VI
        """
        layout_main = QHBoxLayout()
        layout_main.setSpacing(0)
        layout_main.addWidget(self.canvas)
        layout_main.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_main.addStretch(1)

        self.setLayout(layout_main)

    # **************************************************************************************************************** #
    def data_reader_callback(self):
        """
        callback function
        """
        # ------------------------------------------------------------------------------------------------------------ #
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
        # handle data
        # Remove units, spaces, split with coma
        # Refer to documentation of HVPS to assign data to fields
        if line.startswith("AMG88xx") or line.startswith("--") or line.startswith("]") or line == "\r":
            return
        else:

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

                if self.parameters['debug']:
                    print("[TAB] {}".format(self.total_data))

                # UPDATE FIGURE
                # Convertir en une matrice 8x8
                new_data_matrix = np.array(self.total_data, dtype=float).reshape(8, 8)

                self.canvas.update_data(new_data_matrix)

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
        return
