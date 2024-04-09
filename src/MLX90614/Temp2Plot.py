########################################################################################################################
# @project    EPFL-Temp_Setup_#2
# @file       Temp2Plot.py
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
from PyQt6.QtWidgets import *
import pyqtgraph as pg
# custom packages
from src.MLX90614.ColorPlots import *

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)


class Temp2Plot(QWidget):
    def __init__(self, parent=None, plot_tittle=None, scale=None):
        QWidget.__init__(self, parent=parent)

        self.scale = scale

        self.layout_plot = QHBoxLayout(self)
        self.layout_plot.setSpacing(3)

        self.graphics_layout = pg.GraphicsLayoutWidget(show=True)
        # ************************************************************************************************************ #
        # temp plot
        self.temp_plot = self.graphics_layout.addPlot(title=plot_tittle)
        self.temp_plot.setLabel('bottom', 'Time', units='s')
        if self.scale == 'Celsius':
            self.temp_plot.setLabel('left', 'Temp.', units='°C')
            self.temp_plot.setYRange(0, 120)
        elif self.scale == 'Fahrenheit':
            self.temp_plot.setLabel('left', 'Temp.', units='°F')
            self.temp_plot.setYRange(0, 250)

        # ------------------------------------------------------------------------------------------------------------ #
        # V_set // V_vm
        self.t_ambient_plot = self.temp_plot.plot(pen=color[2], name="Temp. Ambient")
        self.t_object_plot = self.temp_plot.plot(pen=color[0], name="Temp. Object")
        # ************************************************************************************************************ #
        # voltage labels
        # ------------------------------------------------------------------------------------------------------------ #
        # Vhv_set
        self.ambient_name_label = QLabel("Ambient")
        self.ambient_name_label.setStyleSheet("background-color: rgb{}; color: white" .format(color[2]))
        self.ambient_name_label.setFixedWidth(60)

        if self.scale == 'Celsius':
            self.ambient_value_label = QLabel("0 °C")
        elif self.scale == 'Fahrenheit':
            self.ambient_value_label = QLabel("0 °F")
        self.ambient_value_label.setFixedWidth(60)
        # ------------------------------------------------------------------------------------------------------------ #
        # Vhv_vm
        self.object_name_label = QLabel("Object")
        self.object_name_label.setStyleSheet("background-color: rgb{}; color: white" .format(color[0]))
        self.object_name_label.setFixedWidth(60)

        if self.scale == 'Celsius':
            self.object_value_label = QLabel("0 °C")
        elif self.scale == 'Fahrenheit':
            self.object_value_label = QLabel("0 °F")
        self.object_value_label.setFixedWidth(60)
        # ------------------------------------------------------------------------------------------------------------ #
        # Vhv_err
        self.err_name_label = QLabel("Error")
        self.err_name_label.setStyleSheet("background-color: rgb{}; color: white" .format(color[9]))
        self.err_name_label.setFixedWidth(60)

        if self.scale == 'Celsius':
            self.err_value_label = QLabel("0 °C")
        elif self.scale == 'Fahrenheit':
            self.err_value_label = QLabel("0 °F")
        self.err_value_label.setFixedWidth(60)
        # ------------------------------------------------------------------------------------------------------------ #
        self.temp_labels_layout = QVBoxLayout(self)
        self.temp_labels_layout.addWidget(self.ambient_name_label, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.temp_labels_layout.addWidget(self.ambient_value_label, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # self.voltage_labels_layout.addSpacerItem(QSpacerItem(10, 16))
        self.temp_labels_layout.addWidget(self.object_name_label, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.temp_labels_layout.addWidget(self.object_value_label, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # self.voltage_labels_layout.addSpacerItem(QSpacerItem(10, 16))
        self.temp_labels_layout.addWidget(self.err_name_label, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.temp_labels_layout.addWidget(self.err_value_label, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.temp_labels_layout.addSpacerItem(QSpacerItem(10, 16))
        self.temp_labels_layout.addStretch(1)
        # ------------------------------------------------------------------------------------------------------------ #
        self.layout_plot.addWidget(self.graphics_layout)
        self.layout_plot.addLayout(self.temp_labels_layout)

    ####################################################################################################################
    def update_plot(self, t, y1, y2):
        self.t_ambient_plot.setData(t, y1)  # plot
        self.t_object_plot.setData(t, y2)

    ####################################################################################################################
    def update_label(self, label1, label2, label3):
        if self.scale == 'Celsius':
            self.ambient_value_label.setText("{} °C".format(label1, '4.2f'))
            self.object_value_label.setText("{} °C".format(label2, '4.2f'))
            self.err_value_label.setText("{} °C".format(label3, '4.2f'))
        elif self.scale == 'Fahrenheit':
            self.ambient_value_label.setText("{} °F".format(label1, '4.2f'))
            self.object_value_label.setText("{} °F".format(label2, '4.2f'))
            self.err_value_label.setText("{} °F".format(label3, '4.2f'))
