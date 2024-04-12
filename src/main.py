########################################################################################################################
# @project    EPFL-Herb_Sensors
# @file       src\main.py
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
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from os.path import *
import sys
# custom packages
from src.ComSelect import ComSelect
from src.devices.AMG8833 import pixel_test
from src.devices.HC_SR04 import HC_SR04_Simple
from src.devices.MLX90614 import mlxtest
from src.devices.VL53L4CD import VL53L4CD_Sat_HelloWorld
from src.Userdef import *

fw_mods = True


########################################################################################################################
def resource_path(relative_path):
    """
    Method that get the correct path for icon and other dependencies of the program as
    a function of whether it is frozen in an executable package.
    :param relative_path: Relative path of the resource
    :return: Absolute path of the resource
    """
    if getattr(sys, 'frozen', False):
        return join(dirname(sys.executable), relative_path)
    return join(abspath('cmd'), relative_path)


class MainTask(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        # ------------------------------------------------------------------------------------------------------------ #
        # open a dialog to ask port
        dialog = ComSelect("")
        if not dialog.exec():
            print("[ERR] Canceled")
            sys.exit(0)

        # ------------------------------------------------------------------------------------------------------------ #
        # get user choices
        self.settings = dialog.get_settings()

        groupbox_text = None
        width = 0
        height = 0

        # ------------------------------------------------------------------------------------------------------------ #
        # Estimation of data rate transmission used for nice beginning of plot and not totally inaccurate time basis
        # on plots
        self.time = 0
        self.estimateRate = 0

        # ------------------------------------------------------------------------------------------------------------ #
        if self.settings['setup'] == "devices":
            groupbox_text = "Thermal cam devices"
            width = 1000
            height = 1000

            # if custom firmware, wait 1000ms between next reception, else wait 100ms
            self.time = 5 if fw_mods else 100
            self.setup = pixel_test(settings=self.settings)

        # ------------------------------------------------------------------------------------------------------------ #
        elif self.settings['setup'] == "MLX90614":
            groupbox_text = "Thermal sensor MLX90614"
            width = 1200
            height = 500

            # if custom firmware, wait only 100ms between next reception, else wait 500ms
            self.time = 100 if fw_mods else 500
            self.estimateRate = 0.1 if fw_mods else 0.5
            self.setup = mlxtest(settings=self.settings, estimate_rate=self.estimateRate)

        # ------------------------------------------------------------------------------------------------------------ #
        elif self.settings['setup'] == "VL53L4CD":
            groupbox_text = "Distance Sensor VL53L4CD"
            width = 1200
            height = 500

            self.time = 200
            self.estimateRate = 0.2
            self.DxBoard = VL53L4CD_Sat_HelloWorld(settings=self.settings, estimate_rate=self.estimateRate)

        # ------------------------------------------------------------------------------------------------------------ #
        elif self.settings['setup'] == "HC-SR04":
            groupbox_text = "Distance Sensor HC-SR04"
            width = 1200
            height = 500

            self.time = 250
            self.estimateRate = 0.25
            self.setup = HC_SR04_Simple(settings=self.settings, estimate_rate=self.estimateRate)

        # ------------------------------------------------------------------------------------------------------------ #
        # INITIALIZE PROGRAM

        groupbox = QGroupBox(groupbox_text)
        groupbox.setStyleSheet('QGroupBox {font-weight: bold;}')
        groupbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        groupbox.setFixedWidth(width)
        groupbox.setFixedHeight(height)

        horizontal_layout = QHBoxLayout(groupbox)
        horizontal_layout.addWidget(self.setup)
        groupbox.setLayout(horizontal_layout)

        self.setup.init_vi()

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(groupbox)
        vertical_layout.addStretch(1)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.addLayout(vertical_layout)
        self.main_layout.addStretch(1)

        self.setWindowTitle("{} - {}".format(PROGRAM_NAME, PROGRAM_VERSION))
        self.setGeometry(0, 0, width, height)
        self.show()

        # ------------------------------------------------------------------------------------------------------------ #
        # set a timer with the callback function which reads data from serial port and plot
        # period is 500ms => 2Hz, if enough data sent by the board
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_reader_callback)
        self.timer.start(self.time)

    # **************************************************************************************************************** #
    def data_reader_callback(self):
        self.setup.data_reader_callback()

    # **************************************************************************************************************** #
    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Window Close", "Are you sure you want to close the window?")

        if reply == QMessageBox.StandardButton.Yes:
            self.setup.stop_comm()

            event.accept()
            if self.settings['debug']:
                print("[INFO] Program closed.")

        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(PROGRAM_NAME)
    app.setWindowIcon(QIcon('epfl_icon.ico'))

    window = MainTask()
    window.show()

    app.exec()


if __name__ == '__main__':
    main()
