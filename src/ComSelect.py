########################################################################################################################
# @project    EPFL-Temp_Setup_#2
# @file       src\ComSelect.py
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
from PyQt6.QtSerialPort import *
from PyQt6.QtWidgets import *


########################################################################################################################
class ComSelect(QDialog):
    """
    This class is a dialog window asking the user for COM port
    """

    def __init__(self, default_search=""):
        super(ComSelect, self).__init__(None)

        # ------------------------------------------------------------------------------------------------------------ #
        # PCB parameters
        self.settings = {
            'setup': '',
            'com_port': '',
            'scales': '',
            't_min': 0.0,
            't_max': 0.0,
            'debug':  True,
            'record':  False,
        }

        # ------------------------------------------------------------------------------------------------------------ #
        # Captor(s) selection
        setup_groupbox = QGroupBox("Sensor")
        setup_groupbox.setStyleSheet('QGroupBox {font-weight: bold;}')

        # ------------------------------------------------------------------------------------------------------------ #
        # list all available captor solutions in the combobox
        self.setup_comboBox = QComboBox(self)
        self.setup_comboBox.addItems(('Temp. #1 (AMG8833)', 'Temp. #2 (MLX90614)',
                                      'Dist. #1 (VL53L4CD)', 'Dist. #2 (HC-SR04)'))
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
        self.scales_comboBox.addItem("Celsius")
        self.scales_comboBox.setEnabled(False)
        self.setup_comboBox.currentTextChanged.connect(self.update_scale_combo)
        # ------------------------------------------------------------------------------------------------------------ #
        t_min_name = QLabel("T. Min (°C):")
        t_min_name.setFixedWidth(80)

        self.t_min_edit = QLineEdit("20")
        self.t_min_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.t_min_edit.setFixedWidth(50)

        t_max_name = QLabel("T. Max (°C):")
        t_max_name.setFixedWidth(80)

        self.t_max_edit = QLineEdit("40")
        self.t_max_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.t_max_edit.setFixedWidth(50)

        range_layout = QHBoxLayout()
        range_layout.addWidget(t_min_name)
        range_layout.addWidget(self.t_min_edit)
        range_layout.addWidget(t_max_name)
        range_layout.addWidget(self.t_max_edit)

        # ------------------------------------------------------------------------------------------------------------ #
        setup_layout = QFormLayout(setup_groupbox)
        setup_layout.addRow("Setup:", self.setup_comboBox)
        setup_layout.addRow("Units:", self.scales_comboBox)
        setup_layout.addRow(range_layout)
        setup_layout.addRow(QLabel(""))
        setup_layout.addRow("Board:", self.com_port_comboBox)
        self.board_instruction_label = QLabel("Please select COM port with description: 'CSP2102'")
        setup_layout.addRow(self.board_instruction_label)
        setup_layout.addRow(QLabel("Try to disconnect and reconnect microcontroller if unable to ""connect\n"))
        setup_groupbox.setLayout(setup_layout)
        # ************************************************************************************************************ #
        # Option(s) selection
        options_groupbox = QGroupBox("Options")
        options_groupbox.setStyleSheet('QGroupBox {font-weight: bold;}')

        # ------------------------------------------------------------------------------------------------------------ #
        # check box for debug mode
        self.debug_checkBox = QCheckBox()
        self.debug_checkBox.setChecked(True)
        self.debug_checkBox.setFixedWidth(15)

        debug_label = QLabel("Debug mode")
        debug_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        debug_label.setFixedWidth(100)
        # ------------------------------------------------------------------------------------------------------------ #
        # check box to record data
        self.record_checkBox = QCheckBox()
        self.record_checkBox.setChecked(False)
        self.record_checkBox.setFixedWidth(15)

        record_label = QLabel("Record data")
        record_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        record_label.setFixedWidth(100)
        # ------------------------------------------------------------------------------------------------------------ #
        options_layout = QHBoxLayout(options_groupbox)
        options_layout.addWidget(self.debug_checkBox)
        options_layout.addWidget(debug_label)
        options_layout.addWidget(self.record_checkBox)
        options_layout.addWidget(record_label)
        options_groupbox.setLayout(options_layout)

        # ------------------------------------------------------------------------------------------------------------ #
        # Button to confirm selections
        self.button_box = QDialogButtonBox()
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        self.button_box.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button_box)

        # ------------------------------------------------------------------------------------------------------------ #
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(setup_groupbox)
        self.main_layout.addWidget(options_groupbox)
        self.main_layout.addLayout(button_layout)

        # ------------------------------------------------------------------------------------------------------------ #
        # Window size
        self.setGeometry(0, 0, 450, 100)

    # **************************************************************************************************************** #
    def update_scale_combo(self, text):
        """
        Updates comboBox depending on others comboBox
        """
        self.scales_comboBox.clear()
        if text == "Temp. #1 (AMG8833)":
            self.scales_comboBox.addItem('Celsius')
            self.scales_comboBox.setEnabled(False)
            self.t_min_edit.setEnabled(True)
            self.t_max_edit.setEnabled(True)
            self.board_instruction_label.setText("Please select COM port with description: 'CP210x'")
        elif text == "Temp. #2 (MLX90614)":
            self.scales_comboBox.addItems(('Celsius', 'Fahrenheit'))
            self.scales_comboBox.setEnabled(True)
            self.t_min_edit.setEnabled(False)
            self.t_max_edit.setEnabled(False)
            self.board_instruction_label.setText("Please select COM port with description: 'Arduino Micro'")
        elif text == "Dist. #1 (VL53L4CD)":
            self.scales_comboBox.addItem('Millimeters')
            self.scales_comboBox.setEnabled(False)
            self.t_min_edit.setEnabled(False)
            self.t_max_edit.setEnabled(False)
            self.board_instruction_label.setText("Please select one of COM ports with description: 'USB Serial Device'")
        elif text == "Dist. #2 (HC-SR04)":
            self.scales_comboBox.addItem('Centimeters')
            self.scales_comboBox.setEnabled(False)
            self.t_min_edit.setEnabled(False)
            self.t_max_edit.setEnabled(False)
            self.board_instruction_label.setText("Please select COM port with description: 'Arduino Micro'")

    # **************************************************************************************************************** #
    def get_settings(self):
        """
        Get settings chosen by user
        """
        match self.setup_comboBox.currentIndex():
            case 0:
                self.settings['setup'] = "devices"
            case 1:
                self.settings['setup'] = "MLX90614"
            case 2:
                self.settings['setup'] = "VL53L4CD"
            case 3:
                self.settings['setup'] = "HC-SR04"

        # get com port chosen by user
        self.settings['com_port'] = self.com_port_comboBox.currentText().split(" ")[0]

        # get scales chosen by user
        self.settings['scales'] = self.scales_comboBox.currentText()

        # get range chosen by user
        self.settings['t_min'] = int(self.t_min_edit.text())
        self.settings['t_max'] = int(self.t_max_edit.text())

        # get debug status chosen by user
        self.settings['debug'] = self.debug_checkBox.isChecked()

        # get record status chosen by user
        self.settings['record'] = self.record_checkBox.isChecked()

        if self.settings['debug']:
            print("[INFO] Setup: {}".format(self.settings['setup']))
            print("[INFO] Units: {}".format(self.settings['scales']))
            print("[INFO] Com port {}".format(self.settings['com_port']))
            print("[INFO] Debug: {}".format(self.settings['debug']))
            print("[INFO] Record: {}".format(self.settings['record']))

        return self.settings
