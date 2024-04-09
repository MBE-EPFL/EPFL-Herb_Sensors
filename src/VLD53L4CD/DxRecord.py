########################################################################################################################
# @project    EPFL-Temp_Setup_#2
# @file       Temp2Record.py
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
from datetime import *
from pathlib import *
from PyQt6.QtWidgets import *
# custom packages
from src.Userdef import *


class DxRecord(QWidget):
    def __init__(self, parent=None, port_name=None):

        QWidget.__init__(self, parent=parent)

        folder = Path("logs")
        folder.mkdir(parents=True, exist_ok=True)

        print("[INFO] Recording data.")
        self.filename = folder.joinpath("DxSetup_log_{}.csv".format(datetime.now().strftime("%Y%m%d-%Hh%M.%S")))

        self.file = open(self.filename, 'w')
        self.file.write("Date, {}\r\n".format(datetime.now().strftime("%Y %m %d - %H:%M:%S")))
        self.file.write("Interface,{},{}\n".format(PROGRAM_NAME, PROGRAM_VERSION))
        self.file.write("Distance Setup\n")
        self.file.write("Port,{}\r\n".format(port_name))
        self.file.write("Time, Status, Distance (mm), Signal (kcps/spad)\r\n")

        self.data_save_label = QLabel("Saving file to: {}".format(self.filename.as_posix()))
        data_save_layout = QVBoxLayout()
        data_save_layout.addWidget(self.data_save_label)

    def save_data(self, status=None, distance=None, signal=None):
        self.file.write("{}, {}, {}, {}\n".format(datetime.now().strftime("%H:%M:%S:%f"), status, distance, signal))

    def close_record(self):
        self.file.close()
        print("[INFO] Data saved to: {}".format(self.filename))
