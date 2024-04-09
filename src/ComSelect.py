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
from PyQt6.QtCore import *
from PyQt6.QtSerialPort import *
from PyQt6.QtWidgets import *


class ComSelect(QDialog):
    """
    This class is a dialog window asking the user for COM port
    """

    def __init__(self, default_search=""):
        super(ComSelect, self).__init__(None)

        self.main_layout = QVBoxLayout(self)

        # ************************************************************************************************************ #
        # Captor(s) selection
        self.setup_groupBox = QGroupBox("Sensor")
        self.setup_groupBox.setStyleSheet('QGroupBox {font-weight: bold;}')
        self.main_layout.addWidget(self.setup_groupBox)
        # ------------------------------------------------------------------------------------------------------------ #
        # list all available captor solutions in the combobox
        self.setup_comboBox = QComboBox(self)
        self.setup_comboBox.addItems(('Temp. #1', 'Temp. #2', 'Distance'))
        # ------------------------------------------------------------------------------------------------------------ #
        # all available com ports, with the most probable one on top
        com_ports = QSerialPortInfo.availablePorts()
        com_ports11 = ["{} {}".format(x.systemLocation(), x.description()) for x in com_ports if default_search in
                       x.description()]
        com_ports12 = ["{} {}".format(x.systemLocation(), x.description()) for x in com_ports if default_search not in
                       x.description()]
        # ------------------------------------------------------------------------------------------------------------ #
        # list all available com port in the combobox for board #1
        self.com_port_comboBox = QComboBox(self)
        self.com_port_comboBox.addItems(com_ports11)
        self.com_port_comboBox.addItems(com_ports12)
        # ------------------------------------------------------------------------------------------------------------ #
        # list all available scales in the combobox for current(s) display(s)
        self.scales_comboBox = QComboBox(self)
        self.scales_comboBox.addItems(('Celsius', 'Fahrenheit'))
        self.setup_comboBox.currentTextChanged.connect(self.update_scale_combo)
        # ------------------------------------------------------------------------------------------------------------ #
        self.setup_groupBox_layout = QFormLayout(self)
        self.setup_groupBox_layout.addRow("Setup:", self.setup_comboBox)
        self.setup_groupBox_layout.addRow("Units:", self.scales_comboBox)
        self.setup_groupBox_layout.addRow(QLabel(""))
        self.setup_groupBox_layout.addRow("Board:", self.com_port_comboBox)
        self.board_instruction_label = QLabel("Please select COM port with description: 'CSP2102'")
        self.setup_groupBox_layout.addRow(self.board_instruction_label)
        self.setup_groupBox_layout.addRow(QLabel("Try to disconnect and reconnect microcontroller if unable to "
                                                 "connect\n"))
        self.setup_groupBox.setLayout(self.setup_groupBox_layout)
        # ************************************************************************************************************ #
        # Option(s) selection
        self.options_groupBox = QGroupBox("Options")
        self.options_groupBox.setStyleSheet('QGroupBox {font-weight: bold;}')
        self.main_layout.addWidget(self.options_groupBox)
        # ------------------------------------------------------------------------------------------------------------ #
        # check box for debug mode
        self.debug_checkBox = QCheckBox()
        self.debug_checkBox.setChecked(True)
        self.debug_checkBox.setFixedWidth(15)
        self.debug_checkBox_title_lbl = QLabel("Debug mode")
        self.debug_checkBox_title_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.debug_checkBox_title_lbl.setFixedWidth(100)
        # ------------------------------------------------------------------------------------------------------------ #
        # check box to record data
        self.record_checkBox = QCheckBox()
        self.record_checkBox.setChecked(False)
        self.record_checkBox.setFixedWidth(15)
        self.record_checkBox_title_lbl = QLabel("Record data")
        self.record_checkBox_title_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.record_checkBox_title_lbl.setFixedWidth(100)
        # ------------------------------------------------------------------------------------------------------------ #
        self.option_groupBox_layout = QHBoxLayout(self)
        self.option_groupBox_layout.addWidget(self.debug_checkBox)
        self.option_groupBox_layout.addWidget(self.debug_checkBox_title_lbl)
        self.option_groupBox_layout.addWidget(self.record_checkBox)
        self.option_groupBox_layout.addWidget(self.record_checkBox_title_lbl)
        self.options_groupBox.setLayout(self.option_groupBox_layout)
        # ************************************************************************************************************ #
        # Button to confirm selections
        self.button_layout = QFormLayout(self)
        self.main_layout.addLayout(self.button_layout)
        # ------------------------------------------------------------------------------------------------------------ #
        self.button_box = QDialogButtonBox()
        # self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        # ------------------------------------------------------------------------------------------------------------ #
        self.button_box.clicked.connect(self.accept)
        # ------------------------------------------------------------------------------------------------------------ #
        self.button_layout.addRow(self.button_box)
        # ************************************************************************************************************ #
        # Window size
        self.setGeometry(100, 100, 450, 100)

    ####################################################################################################################
    def update_scale_combo(self, text):
        self.scales_comboBox.clear()
        if text == "Temp. #1":
            self.scales_comboBox.addItems(('Celsius', 'Fahrenheit'))
            self.scales_comboBox.setEnabled(True)
            self.board_instruction_label.setText("Please select COM port with description: 'CP210x'")
        elif text == "Temp. #2":
            self.scales_comboBox.addItems(('Celsius', 'Fahrenheit'))
            self.scales_comboBox.setEnabled(True)
            self.board_instruction_label.setText("Please select COM port with description: 'Arduino Micro'")
        elif text == "Distance":
            self.scales_comboBox.addItem('Millimeters')
            self.scales_comboBox.setEnabled(False)
            self.board_instruction_label.setText("Please select one of COM ports with description: 'USB Serial Device'")

    ####################################################################################################################
    def get_setup(self):
        return self.setup_comboBox.currentText()

    ####################################################################################################################
    def get_com_port(self):
        return self.com_port_comboBox.currentText().split(" ")[0]

    ####################################################################################################################
    def get_scales(self):
        return self.scales_comboBox.currentText()

    ####################################################################################################################
    def get_debug_status(self):
        return self.debug_checkBox.isChecked()

    ####################################################################################################################
    def get_record_status(self):
        return self.record_checkBox.isChecked()
