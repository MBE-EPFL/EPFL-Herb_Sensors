########################################################################################################################
# @project    EPFL-Herb_Sensors
# @file       MLX90614\Temp2Record.py
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
from datetime import *
from pathlib import *
from PyQt6.QtWidgets import *
# custom packages
from src.Userdef import *


class Temp2Record(QWidget):
    def __init__(self, parent=None, parameters=None):

        QWidget.__init__(self, parent=parent)

        folder = Path("logs")
        folder.mkdir(parents=True, exist_ok=True)

        print("[INFO] Recording data.")
        self.filename = folder.joinpath("Temp2Setup_log_{}.csv".format(datetime.now().strftime("%Y%m%d-%Hh%M.%S")))

        self.file = open(self.filename, 'w')
        self.file.write("Date, {}\r\n".format(datetime.now().strftime("%Y %m %d - %H:%M:%S")))
        self.file.write("Interface,{},{}\n".format(PROGRAM_NAME, PROGRAM_VERSION))
        self.file.write("Temperature #2 Setup\n")
        self.file.write("Port,{}\r\n".format(parameters['com_port']))
        self.file.write("Time, Ambient, Object, error\r\n")

        self.data_save_label = QLabel("Saving file to: {}".format(self.filename.as_posix()))
        data_save_layout = QVBoxLayout()
        data_save_layout.addWidget(self.data_save_label)

    def save_data(self, t_ambient=None, t_object=None, t_error=None):
        self.file.write("{}, {}, {}, {}\n".format(datetime.now().strftime("%H:%M:%S:%f"), t_ambient, t_object, t_error))

    def close_record(self):
        self.file.close()
        print("[INFO] Data saved to: {}".format(self.filename))
