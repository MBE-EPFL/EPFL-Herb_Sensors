########################################################################################################################
# @project    EPFL-Temp_Setup_#2
# @file       main.py
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
from PyQt6.QtGui import *
from os.path import *
# custom packages
from ComSelect import *
from AMG8833 import *
from MLX90614 import *
from VLD53L4CD import *
from Userdef import *


def resource_path(relative_path):
    """
    Method that get the correct path for icon and other dependencies of the program as
    a function of whether it is frozen in an executable package.
    :param relative_path: Relative path of the resource
    :return: Absolute path of the resource
    """
    if hasattr(sys, '_MEIPASS'):
        return join(sys._MEIPASS, relative_path)
    return join(abspath('.'), relative_path)


class MainTask(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        # open a dialog to ask port
        dialog = ComSelect("")
        if not dialog.exec():
            print("[ERR] Canceled")
            sys.exit(0)
        # ************************************************************************************************************ #
        # COM PORT
        self.setup = dialog.get_setup()
        # ************************************************************************************************************ #
        # COM PORT
        com_port = dialog.get_com_port()
        # ************************************************************************************************************ #
        # SCALES
        scales_selected = dialog.get_scales()
        # ************************************************************************************************************ #
        # DEBUG
        self.debug_mode = dialog.get_debug_status()
        # ************************************************************************************************************ #
        # RECORD DATA
        record_data = dialog.get_record_status()

        # ************************************************************************************************************ #
        # INITIALIZE PROGRAM
        # init user interface + callback for buttons...
        self.setWindowTitle("{} - {}".format(PROGRAM_NAME, PROGRAM_VERSION))

        self.main_layout = QHBoxLayout(self)
        # ************************************************************************************************************ #
        # Temp #1 Setup (= )
        if self.setup == "Temp. #1":
            # -------------------------------------------------------------------------------------------------------- #
            # Estimation of data rate transmission used for nice beginning of plot and not totally inaccurate time basis
            # on plots
            self.time = 100
            # -------------------------------------------------------------------------------------------------------- #
            t_min, t_max = dialog.get_range()
            # -------------------------------------------------------------------------------------------------------- #
            self.Temp1Board = Temp1Setup(port_name=com_port,
                                         debug_mode=self.debug_mode,
                                         t_min=t_min, t_max=t_max)
            # -------------------------------------------------------------------------------------------------------- #
            self.Temp1Setup_groupBox = QGroupBox("Thermal cam")
            self.Temp1Setup_groupBox.setStyleSheet('QGroupBox {font-weight: bold;}')
            self.Temp1Setup_groupBox.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.Temp1Setup_groupBox_layout = QFormLayout(self)
            self.Temp1Setup_groupBox_layout.addRow(self.Temp1Board)
            self.Temp1Setup_groupBox.setLayout(self.Temp1Setup_groupBox_layout)

            self.main_layout.addWidget(self.Temp1Setup_groupBox, 0)

            self.Temp1Board.init_vi()

            self.setGeometry(0, 0, 950, 700)
        # ************************************************************************************************************ #
        # Temp #2 Setup (= MXL90614)
        elif self.setup == "Temp. #2":
            # -------------------------------------------------------------------------------------------------------- #
            # Estimation of data rate transmission used for nice beginning of plot and not totally inaccurate time basis
            # on plots
            self.time = 500
            self.estimateRate = 0.5
            # -------------------------------------------------------------------------------------------------------- #
            self.Temp2Board = Temp2Setup(port_name=com_port,
                                         estimate_rate=self.estimateRate,
                                         scales=scales_selected,
                                         debug_mode=self.debug_mode,
                                         record_data=record_data)
            # -------------------------------------------------------------------------------------------------------- #
            self.Temp2Setup_groupBox = QGroupBox("Thermal sensor")
            self.Temp2Setup_groupBox.setStyleSheet('QGroupBox {font-weight: bold;}')

            self.Temp2Setup_groupBox_layout = QFormLayout(self)
            self.Temp2Setup_groupBox_layout.addRow(self.Temp2Board)
            self.Temp2Setup_groupBox.setLayout(self.Temp2Setup_groupBox_layout)

            self.main_layout.addWidget(self.Temp2Setup_groupBox, 0)

            self.Temp2Board.init_vi()

            self.setGeometry(0, 0, 500, 500)
        # ************************************************************************************************************ #
        # Distance Setup (= )
        elif self.setup == "Distance":
            # -------------------------------------------------------------------------------------------------------- #
            # Estimation of data rate transmission used for nice beginning of plot and not totally inaccurate time basis
            # on plots
            self.time = 200
            self.estimateRate = 0.2
            # -------------------------------------------------------------------------------------------------------- #
            self.DxBoard = DxSetup(port_name=com_port,
                                   estimate_rate=self.estimateRate,
                                   debug_mode=self.debug_mode,
                                   record_data=record_data)
            # -------------------------------------------------------------------------------------------------------- #
            self.DxSetup_groupBox = QGroupBox("Distance Sensor")
            self.DxSetup_groupBox.setStyleSheet('QGroupBox {font-weight: bold;}')

            self.DxSetup_groupBox_layout = QFormLayout(self)
            self.DxSetup_groupBox_layout.addRow(self.DxBoard)
            self.DxSetup_groupBox.setLayout(self.DxSetup_groupBox_layout)

            self.main_layout.addWidget(self.DxSetup_groupBox, 0)

            self.DxBoard.init_vi()

            self.setGeometry(0, 0, 800, 1000)
        # ************************************************************************************************************ #

        self.main_layout.addStretch(1)

        self.show()

        # ************************************************************************************************************ #
        # DEBUG MODE
        if self.debug_mode == 1:
            print("[INFO] Setup: {}".format(self.setup))
            print("[INFO] Units: {}".format(scales_selected))
            print("[INFO] Com port {}".format(com_port))

            print("[INFO] Debug: {}".format(self.debug_mode))
            print("[INFO] Record: {}".format(record_data))

        # ************************************************************************************************************ #
        # set a timer with the callback function which reads data from serial port and plot
        # period is 500ms => 2Hz, if enough data sent by the board
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_reader_callback)
        self.timer.start(self.time)

    ####################################################################################################################
    def data_reader_callback(self):
        if self.setup == "Temp. #1":
            self.Temp1Board.data_reader_callback()
        elif self.setup == "Temp. #2":
            self.Temp2Board.data_reader_callback()
        elif self.setup == "Distance":
            self.DxBoard.data_reader_callback()

    ####################################################################################################################
    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Window Close", "Are you sure you want to close the window?")

        if reply == QMessageBox.StandardButton.Yes:
            if self.setup == "Temp. #2":
                self.Temp2Board.stop_comm()
            elif self.setup == "Distance":
                self.DxBoard.stop_comm()

            event.accept()
            if self.debug_mode == 1:
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
