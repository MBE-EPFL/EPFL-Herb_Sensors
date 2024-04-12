########################################################################################################################
# @project    EPFL-Herb_Sensors
# @file       VLD53L4CD\DxPlot.py
# @brief      Author:             MBE
#             Institute:          EPFL
#             Laboratory:         LMTS
#             Software version:   v1.00
#             Created on:         20.02.2024
#             Last modifications: 09.04.2024
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
from src.plots.ColorPlots import *

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)


class DxPlot(QWidget):
    def __init__(self, parent=None, tittle=None, y_max=0):
        QWidget.__init__(self, parent=parent)

        if tittle == 'Distance':
            self.unit = 'mm'
            self.color_used = color[0]
        elif tittle == 'Signal':
            self.unit = 'kcps/spad'
            self.color_used = color[2]

        # ------------------------------------------------------------------------------------------------------------ #
        # distance plot
        graphics_layout = pg.GraphicsLayoutWidget(show=True)
        dx_plot = graphics_layout.addPlot(title=tittle)
        dx_plot.setLabel('bottom', 'Time', units='s')
        dx_plot.setLabel('left', tittle, units=self.unit)
        dx_plot.setYRange(0, y_max)
        dx_plot.getAxis('left').setRange(0, y_max)

        # distance plot layout
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(graphics_layout)

        self.value_plot = dx_plot.plot(pen=self.color_used, name=tittle)

        # ------------------------------------------------------------------------------------------------------------ #
        name_label = QLabel("{}".format(tittle))
        name_label.setStyleSheet("background-color: rgb{}; color: white".format(self.color_used))
        name_label.setFixedWidth(70)

        self.value_label = QLabel("0 {}".format(self.unit))
        self.value_label.setFixedWidth(70)

        # ------------------------------------------------------------------------------------------------------------ #
        labels_layout = QVBoxLayout()
        labels_layout.addWidget(name_label, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        labels_layout.addWidget(self.value_label, 0, alignment=Qt.AlignmentFlag.AlignRight)
        labels_layout.addSpacerItem(QSpacerItem(10, 16))
        labels_layout.addStretch(1)

        # ------------------------------------------------------------------------------------------------------------ #
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(3)
        main_layout.addLayout(plot_layout)
        main_layout.addLayout(labels_layout)

    ####################################################################################################################
    def update_plot(self, t, y):
        self.value_plot.setData(x=t, y=y)  # plot

    ####################################################################################################################
    def update_label(self, label):
        self.value_label.setText("{} {}".format(label, self.unit))
