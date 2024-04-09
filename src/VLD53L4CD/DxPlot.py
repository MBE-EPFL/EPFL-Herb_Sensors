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
from src.VLD53L4CD.ColorPlots import *

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)


class DxPlot(QWidget):
    def __init__(self, parent=None, plot_tittle=None, y_min=0, y_max=0):
        QWidget.__init__(self, parent=parent)

        self.title = plot_tittle

        self.layout_plot = QHBoxLayout(self)
        self.layout_plot.setSpacing(3)

        self.graphics_layout = pg.GraphicsLayoutWidget(show=True)
        # ************************************************************************************************************ #
        # temp plot
        self.dx_plot = self.graphics_layout.addPlot(title=plot_tittle)
        self.dx_plot.setLabel('bottom', 'Time', units='s')
        if self.title == 'Distance':
            self.dx_plot.setLabel('left', 'Distance', units='mm')
            self.value_plot = self.dx_plot.plot(pen=color[0], name="Distance")
        elif self.title == 'Signal':
            self.dx_plot.setLabel('left', 'Signal', units='kcps/spad')
            self.value_plot = self.dx_plot.plot(pen=color[2], name="Signal")

        self.dx_plot.setYRange(0, y_max)
        self.dx_plot.getAxis('left').setRange(0, y_max)

        # ------------------------------------------------------------------------------------------------------------ #
        # V_set // V_vm
        # ************************************************************************************************************ #
        # voltage labels
        # ------------------------------------------------------------------------------------------------------------ #
        # Vhv_set

        self.name_label = QLabel("{}".format(self.title))

        if self.title == 'Distance':
            self.name_label.setStyleSheet("background-color: rgb{}; color: white".format(color[0]))
            self.value_label = QLabel("0 mm")
        elif self.title == 'Signal':
            self.name_label.setStyleSheet("background-color: rgb{}; color: white".format(color[2]))
            self.value_label = QLabel("0 kcps/spad")

        self.name_label.setFixedWidth(70)
        self.value_label.setFixedWidth(70)

        # ------------------------------------------------------------------------------------------------------------ #
        self.temp_labels_layout = QVBoxLayout(self)
        self.temp_labels_layout.addWidget(self.name_label, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.temp_labels_layout.addWidget(self.value_label, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.temp_labels_layout.addSpacerItem(QSpacerItem(10, 16))
        self.temp_labels_layout.addStretch(1)
        # ------------------------------------------------------------------------------------------------------------ #
        self.layout_plot.addWidget(self.graphics_layout)
        self.layout_plot.addLayout(self.temp_labels_layout)

    ####################################################################################################################
    def update_plot(self, t, y):
        self.value_plot.setData(x=t, y=y)  # plot

    ####################################################################################################################
    def update_label(self, label):
        if self.title == 'Distance':
            self.value_label.setText("{} mm".format(label))
        elif self.title == 'Signal':
            self.value_label.setText("{} kcps/spad".format(label))
