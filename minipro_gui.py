#!/usr/bin/env python3
"""
T48 MiniPro Device Programmer GUI
A PyQt6 frontend for the minipro command-line tool
"""

import sys
import subprocess
import os
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit,
    QFileDialog, QGroupBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QProgressBar, QMessageBox, QListWidget, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QProcess, QTimer, QSettings
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPalette


class CommandThread(QThread):
    """Thread for running minipro commands without blocking the GUI"""
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    finished_signal = pyqtSignal(int)
    progress_update = pyqtSignal(int, str)  # progress percentage and status text
    debug_output = pyqtSignal(str)  # debug information
    
    def __init__(self, command, debug_mode=False):
        super().__init__()
        self.command = command
        self.debug_mode = debug_mode
        
    def parse_progress(self, line):
        """Parse minipro output for progress information"""
        # Strip ANSI escape sequences like [K (clear to end of line)
        clean_line = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line)
        clean_line = clean_line.strip()
        
        # Debug output
        if self.debug_mode:
            self.debug_output.emit(f"[PARSE] Raw: {repr(line.strip())}")
            if clean_line != line.strip():
                self.debug_output.emit(f"[PARSE] Clean: {clean_line}")
        
        # Look for operation start indicators
        if any(word in clean_line.lower() for word in ['reading device', 'reading code', 'reading']):
            if 'chip id' not in clean_line.lower() and 'id:' not in clean_line.lower():
                self.progress_update.emit(5, "Reading device...")
                if self.debug_mode:
                    self.debug_output.emit("[PROGRESS] Detected: Reading operation")
                    
        elif any(word in clean_line.lower() for word in ['writing jedec', 'writing code', 'writing']):
            if 'protection' not in clean_line.lower():
                self.progress_update.emit(5, "Writing to device...")
                if self.debug_mode:
                    self.debug_output.emit("[PROGRESS] Detected: Writing operation")
                    
        elif any(word in clean_line.lower() for word in ['verifying', 'verify']):
            self.progress_update.emit(5, "Verifying...")
            if self.debug_mode:
                self.debug_output.emit("[PROGRESS] Detected: Verifying operation")
                
        elif any(word in clean_line.lower() for word in ['erasing']):
            self.progress_update.emit(5, "Erasing device...")
            if self.debug_mode:
                self.debug_output.emit("[PROGRESS] Detected: Erasing operation")
        
        # Look for percentage patterns like "50%" or "Writing... 50%"
        # This is the key pattern from your output: "Writing jedec file... 50%"
        percent_match = re.search(r'(\d+)\s*%', clean_line)
        if percent_match:
            percentage = int(percent_match.group(1))
            # Extract operation name if present
            operation = "Progress"
            if "writing" in clean_line.lower():
                operation = "Writing"
            elif "reading" in clean_line.lower():
                operation = "Reading"
            elif "verifying" in clean_line.lower():
                operation = "Verifying"
            elif "erasing" in clean_line.lower():
                operation = "Erasing"
            
            self.progress_update.emit(percentage, f"{operation}: {percentage}%")
            if self.debug_mode:
                self.debug_output.emit(f"[PROGRESS] Percentage found: {percentage}% (operation: {operation})")
            
        # Look for byte progress like "1024/4096 bytes" or "1024 / 4096"
        bytes_match = re.search(r'(\d+)\s*[/\s]+\s*(\d+)\s*(?:bytes|B|b)', clean_line, re.IGNORECASE)
        if bytes_match:
            current = int(bytes_match.group(1))
            total = int(bytes_match.group(2))
            if total > 0:
                percentage = int((current / total) * 100)
                self.progress_update.emit(percentage, f"Progress: {current}/{total} bytes")
                if self.debug_mode:
                    self.debug_output.emit(f"[PROGRESS] Bytes found: {current}/{total} -> {percentage}%")
        
        # Look for time completion messages like "3.37 Sec  OK" or "820.3 ms  OK"
        if re.search(r'([\d.]+)\s*(ms|sec|s)\s+ok', clean_line.lower()):
            self.progress_update.emit(100, "Complete!")
            if self.debug_mode:
                self.debug_output.emit("[PROGRESS] Time + OK detected - operation complete")
        
        # Look for completion indicators
        if clean_line.lower().strip() in ['ok', 'verification ok', 'done', 'complete', 'success']:
            self.progress_update.emit(100, "Complete!")
            if self.debug_mode:
                self.debug_output.emit("[PROGRESS] Completion detected")
        
        # Look for "Verification OK" specifically
        if 'verification ok' in clean_line.lower():
            self.progress_update.emit(100, "Verification OK!")
            if self.debug_mode:
                self.debug_output.emit("[PROGRESS] Verification success detected")
        
    def run(self):
        try:
            # Force unbuffered output using stdbuf if available
            command = self.command
            
            # Try to use stdbuf for unbuffered output (Linux)
            import shutil
            if shutil.which('stdbuf'):
                command = f"stdbuf -o0 -e0 {self.command}"
            
            # Keep stdout and stderr SEPARATE
            # minipro outputs progress to STDERR!
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  # Keep separate!
                text=True,
                bufsize=0,
                universal_newlines=True
            )
            
            import select
            import sys
            
            # Use select to read from both pipes without blocking
            # (Unix-like systems only)
            if hasattr(select, 'select'):
                current_line_out = ""
                current_line_err = ""
                
                while True:
                    # Check which streams have data
                    readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
                    
                    for stream in readable:
                        char = stream.read(1)
                        if not char:
                            continue
                        
                        # Build lines from stderr (progress) and stdout (normal output)
                        if stream == process.stderr:
                            current_line_err += char
                            if char in ['\n', '\r']:
                                if current_line_err.strip():
                                    self.output_received.emit(current_line_err)
                                    self.parse_progress(current_line_err)
                                current_line_err = ""
                        else:  # stdout
                            current_line_out += char
                            if char in ['\n', '\r']:
                                if current_line_out.strip():
                                    self.output_received.emit(current_line_out)
                                current_line_out = ""
                    
                    # Check if process finished
                    if process.poll() is not None:
                        break
                
                # Read any remaining output
                remaining_err = process.stderr.read()
                if remaining_err:
                    for line in remaining_err.split('\n'):
                        if line.strip():
                            self.output_received.emit(line + '\n')
                            self.parse_progress(line)
                            
                remaining_out = process.stdout.read()
                if remaining_out:
                    self.output_received.emit(remaining_out)
                    
            else:
                # Fallback for Windows - use threads
                import threading
                
                def read_stderr():
                    current_line = ""
                    while True:
                        char = process.stderr.read(1)
                        if not char:
                            break
                        current_line += char
                        if char in ['\n', '\r']:
                            if current_line.strip():
                                self.output_received.emit(current_line)
                                self.parse_progress(current_line)
                            current_line = ""
                
                def read_stdout():
                    for line in process.stdout:
                        self.output_received.emit(line)
                
                stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                stdout_thread = threading.Thread(target=read_stdout, daemon=True)
                
                stderr_thread.start()
                stdout_thread.start()
                
                stderr_thread.join()
                stdout_thread.join()
            
            # Wait for process to complete
            returncode = process.wait()
            self.finished_signal.emit(returncode)
            
        except Exception as e:
            self.error_received.emit(f"Error executing command: {str(e)}")
            self.finished_signal.emit(-1)


class MiniProGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_thread = None
        self.device_thread = None
        
        # Initialize settings
        self.settings = QSettings("MiniProGUI", "T48Programmer")
        
        self.init_ui()
        self.populate_common_devices()
        self.restore_settings()
        
    def populate_common_devices(self):
        """Populate dropdown with commonly used devices"""
        common_devices = [
            # EEPROM
            "AT28C64@DIP28", "AT28C256@DIP28", "AT29C256@DIP28", "AT29C512@DIP28",
            # EPROM
            "27C64@DIP28", "27C128@DIP28", "27C256@DIP28", "27C512@DIP28",
            # SPI Flash
            "W25Q32JV@SOIC8", "W25Q64JV@SOIC8", "W25Q128JV@SOIC8",
            "MX25L3206E@SOIC8", "MX25L6406E@SOIC8",
            # GAL/PAL
            "GAL16V8", "GAL16V8D", "GAL20V8", "GAL22V10",
            "GAL16V8@PLCC20", "GAL16V8@DIP20", "GAL20V8@PLCC28",
            # Microcontrollers
            "ATMEGA328P@DIP28", "ATMEGA16@DIP40", "ATMEGA32@DIP40",
            "PIC16F628A@DIP18", "PIC16F84A@DIP18", "PIC16F877A@DIP40",
            # Logic ICs (common for testing)
            "7404@DIP14", "7400@DIP14", "74HC00@DIP14", "74HC04@DIP14",
        ]
        self.device_combo.addItems(sorted(common_devices))
        self.device_combo.setCurrentIndex(-1)  # No selection by default
        
    def restore_settings(self):
        """Restore saved settings"""
        # Restore last used device
        last_device = self.settings.value("last_device", "")
        if last_device:
            self.device_combo.setCurrentText(last_device)
        
        # Restore window geometry
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Restore last used files
        last_read_file = self.settings.value("last_read_file", "")
        if last_read_file:
            self.read_file.setText(last_read_file)
            
        last_write_file = self.settings.value("last_write_file", "")
        if last_write_file:
            self.write_file.setText(last_write_file)
        
        # Restore memory type
        last_memory_type = self.settings.value("last_memory_type", "code")
        index = self.memory_type.findText(last_memory_type)
        if index >= 0:
            self.memory_type.setCurrentIndex(index)
            
        # Restore file format
        last_format = self.settings.value("last_format", "binary (default)")
        index = self.file_format.findText(last_format)
        if index >= 0:
            self.file_format.setCurrentIndex(index)
    
    def save_settings(self):
        """Save current settings"""
        # Save last used device
        self.settings.setValue("last_device", self.device_combo.currentText())
        
        # Save window geometry
        self.settings.setValue("window_geometry", self.saveGeometry())
        
        # Save last used files
        self.settings.setValue("last_read_file", self.read_file.text())
        self.settings.setValue("last_write_file", self.write_file.text())
        
        # Save memory type
        self.settings.setValue("last_memory_type", self.memory_type.currentText())
        
        # Save file format
        self.settings.setValue("last_format", self.file_format.currentText())
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.save_settings()
        event.accept()
        
    def init_ui(self):
        self.setWindowTitle("T48 MiniPro Device Programmer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for tabs and console
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_device_tab(), "Device Info")
        self.tabs.addTab(self.create_read_write_tab(), "Read/Write")
        self.tabs.addTab(self.create_firmware_tab(), "Firmware/Erase")
        self.tabs.addTab(self.create_config_tab(), "Configuration")
        self.tabs.addTab(self.create_advanced_tab(), "Advanced")
        
        splitter.addWidget(self.tabs)
        
        # Create console output
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout()
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Courier", 9))
        self.console.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        
        console_controls = QHBoxLayout()
        clear_btn = QPushButton("Clear Console")
        clear_btn.clicked.connect(self.console.clear)
        console_controls.addWidget(clear_btn)
        
        self.debug_mode = QCheckBox("Debug Mode (show parsing)")
        self.debug_mode.setToolTip("Show detailed progress parsing information")
        console_controls.addWidget(self.debug_mode)
        
        console_controls.addStretch()
        
        console_layout.addLayout(console_controls)
        console_layout.addWidget(self.console)
        
        # Add progress bar
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        console_layout.addLayout(progress_layout)
        console_group.setLayout(console_layout)
        
        splitter.addWidget(console_group)
        splitter.setSizes([500, 300])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def create_device_tab(self):
        """Device detection and information tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Programmer info group
        prog_group = QGroupBox("Programmer Information")
        prog_layout = QVBoxLayout()
        
        prog_buttons = QHBoxLayout()
        
        detect_btn = QPushButton("Detect Programmer")
        detect_btn.clicked.connect(self.detect_programmer)
        prog_buttons.addWidget(detect_btn)
        
        query_btn = QPushButton("Query Supported Programmers")
        query_btn.clicked.connect(self.query_supported)
        prog_buttons.addWidget(query_btn)
        
        hw_check_btn = QPushButton("Hardware Check")
        hw_check_btn.clicked.connect(self.hardware_check)
        prog_buttons.addWidget(hw_check_btn)
        
        prog_layout.addLayout(prog_buttons)
        prog_group.setLayout(prog_layout)
        layout.addWidget(prog_group)
        
        # Device selection group
        device_group = QGroupBox("Device Selection")
        device_layout = QVBoxLayout()
        
        info_label = QLabel("💡 Common devices pre-loaded. Type to search or click 'Load Device List' for all 13,000+ devices")
        info_label.setStyleSheet("color: #64b5f6; font-style: italic;")
        info_label.setWordWrap(True)
        device_layout.addWidget(info_label)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Select Device:"))
        
        # Searchable dropdown
        self.device_combo = QComboBox()
        self.device_combo.setEditable(True)
        self.device_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.device_combo.setPlaceholderText("Type to search (e.g., AT29C256)...")
        self.device_combo.setMinimumWidth(400)
        
        # Enable filtering
        self.device_combo.setDuplicatesEnabled(False)
        self.device_combo.completer().setCompletionMode(
            self.device_combo.completer().CompletionMode.PopupCompletion
        )
        self.device_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        
        search_layout.addWidget(self.device_combo)
        
        refresh_btn = QPushButton("Load Device List")
        refresh_btn.setToolTip("Load all supported devices (may take a moment)")
        refresh_btn.clicked.connect(self.load_device_list)
        search_layout.addWidget(refresh_btn)
        
        device_layout.addLayout(search_layout)
        
        # Quick actions
        quick_layout = QHBoxLayout()
        
        device_info_btn = QPushButton("Get Device Info")
        device_info_btn.clicked.connect(self.get_device_info)
        quick_layout.addWidget(device_info_btn)
        
        clear_btn = QPushButton("Clear Selection")
        clear_btn.clicked.connect(lambda: self.device_combo.clearEditText())
        quick_layout.addWidget(clear_btn)
        
        quick_layout.addStretch()
        device_layout.addLayout(quick_layout)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # Chip operations group
        chip_group = QGroupBox("Chip Operations")
        chip_layout = QHBoxLayout()
        
        read_id_btn = QPushButton("Read Chip ID")
        read_id_btn.clicked.connect(self.read_chip_id)
        chip_layout.addWidget(read_id_btn)
        
        pin_check_btn = QPushButton("Pin Contact Check")
        pin_check_btn.clicked.connect(self.pin_check)
        chip_layout.addWidget(pin_check_btn)
        
        blank_check_btn = QPushButton("Blank Check")
        blank_check_btn.clicked.connect(self.blank_check)
        chip_layout.addWidget(blank_check_btn)
        
        chip_group.setLayout(chip_layout)
        layout.addWidget(chip_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_read_write_tab(self):
        """Read/Write operations tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Memory type selection
        mem_group = QGroupBox("Memory Type")
        mem_layout = QHBoxLayout()
        mem_layout.addWidget(QLabel("Memory Type:"))
        self.memory_type = QComboBox()
        self.memory_type.addItems(["code", "data", "config", "user", "calibration"])
        mem_layout.addWidget(self.memory_type)
        mem_layout.addStretch()
        mem_group.setLayout(mem_layout)
        layout.addWidget(mem_group)
        
        # File format
        format_group = QGroupBox("File Format")
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.file_format = QComboBox()
        self.file_format.addItems(["binary (default)", "ihex", "srec"])
        format_layout.addWidget(self.file_format)
        format_layout.addStretch()
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Read operations
        read_group = QGroupBox("Read from Device")
        read_layout = QVBoxLayout()
        
        read_file_layout = QHBoxLayout()
        read_file_layout.addWidget(QLabel("Output File:"))
        self.read_file = QLineEdit()
        read_file_layout.addWidget(self.read_file)
        
        read_browse = QPushButton("Browse...")
        read_browse.clicked.connect(lambda: self.browse_file(self.read_file, save=True))
        read_file_layout.addWidget(read_browse)
        
        read_layout.addLayout(read_file_layout)
        
        read_buttons = QHBoxLayout()
        read_btn = QPushButton("Read Device")
        read_btn.clicked.connect(self.read_device)
        read_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        read_buttons.addWidget(read_btn)
        
        self.skip_id_check = QCheckBox("Skip ID Check")
        read_buttons.addWidget(self.skip_id_check)
        
        read_buttons.addStretch()
        read_layout.addLayout(read_buttons)
        read_group.setLayout(read_layout)
        layout.addWidget(read_group)
        
        # Write operations
        write_group = QGroupBox("Write to Device")
        write_layout = QVBoxLayout()
        
        write_file_layout = QHBoxLayout()
        write_file_layout.addWidget(QLabel("Input File:"))
        self.write_file = QLineEdit()
        write_file_layout.addWidget(self.write_file)
        
        write_browse = QPushButton("Browse...")
        write_browse.clicked.connect(lambda: self.browse_file(self.write_file, save=False))
        write_file_layout.addWidget(write_browse)
        
        write_layout.addLayout(write_file_layout)
        
        # Write options
        write_opts = QHBoxLayout()
        self.skip_erase = QCheckBox("Skip Erase")
        write_opts.addWidget(self.skip_erase)
        
        self.skip_verify = QCheckBox("Skip Verify")
        write_opts.addWidget(self.skip_verify)
        
        self.no_id_error = QCheckBox("No ID Error")
        write_opts.addWidget(self.no_id_error)
        
        self.no_size_error = QCheckBox("No Size Error")
        write_opts.addWidget(self.no_size_error)
        
        write_opts.addStretch()
        write_layout.addLayout(write_opts)
        
        write_buttons = QHBoxLayout()
        write_btn = QPushButton("Write to Device")
        write_btn.clicked.connect(self.write_device)
        write_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        write_buttons.addWidget(write_btn)
        
        verify_btn = QPushButton("Verify Device")
        verify_btn.clicked.connect(self.verify_device)
        write_buttons.addWidget(verify_btn)
        
        erase_btn = QPushButton("Erase Device")
        erase_btn.clicked.connect(self.erase_device)
        erase_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        write_buttons.addWidget(erase_btn)
        
        write_buttons.addStretch()
        write_layout.addLayout(write_buttons)
        
        write_group.setLayout(write_layout)
        layout.addWidget(write_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_firmware_tab(self):
        """Firmware and erase operations tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Erase operations
        erase_group = QGroupBox("Erase Operations")
        erase_layout = QVBoxLayout()
        
        erase_info = QLabel("⚠️ Warning: Erasing will permanently delete all data on the device!")
        erase_info.setStyleSheet("color: #ff9800; font-weight: bold;")
        erase_layout.addWidget(erase_info)
        
        erase_buttons = QHBoxLayout()
        erase_btn = QPushButton("Erase Device")
        erase_btn.clicked.connect(self.erase_device)
        erase_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        erase_buttons.addWidget(erase_btn)
        erase_buttons.addStretch()
        
        erase_layout.addLayout(erase_buttons)
        erase_group.setLayout(erase_layout)
        layout.addWidget(erase_group)
        
        # Firmware update
        firmware_group = QGroupBox("Firmware Update")
        firmware_layout = QVBoxLayout()
        
        fw_info = QLabel("Update the T48 programmer firmware.\n"
                        "Use UpdateT48.dat file from manufacturer.")
        firmware_layout.addWidget(fw_info)
        
        fw_file_layout = QHBoxLayout()
        fw_file_layout.addWidget(QLabel("Firmware File:"))
        self.firmware_file = QLineEdit()
        fw_file_layout.addWidget(self.firmware_file)
        
        fw_browse = QPushButton("Browse...")
        fw_browse.clicked.connect(lambda: self.browse_file(self.firmware_file, save=False, 
                                                           filter="Firmware Files (*.dat);;All Files (*)"))
        fw_file_layout.addWidget(fw_browse)
        
        firmware_layout.addLayout(fw_file_layout)
        
        fw_buttons = QHBoxLayout()
        fw_update_btn = QPushButton("Update Firmware")
        fw_update_btn.clicked.connect(self.update_firmware)
        fw_update_btn.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold;")
        fw_buttons.addWidget(fw_update_btn)
        fw_buttons.addStretch()
        
        firmware_layout.addLayout(fw_buttons)
        firmware_group.setLayout(firmware_layout)
        layout.addWidget(firmware_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_config_tab(self):
        """Configuration and voltage settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Voltage settings
        voltage_group = QGroupBox("Voltage Settings (T48)")
        voltage_layout = QVBoxLayout()
        
        vpp_layout = QHBoxLayout()
        vpp_layout.addWidget(QLabel("VPP (Programming):"))
        self.vpp_voltage = QComboBox()
        self.vpp_voltage.addItems(["Default", "9", "9.5", "10", "11", "11.5", "12", "12.5", 
                                   "13", "13.5", "14", "14.5", "15.5", "16", "16.5", "17", "18", "21", "25"])
        vpp_layout.addWidget(self.vpp_voltage)
        vpp_layout.addStretch()
        voltage_layout.addLayout(vpp_layout)
        
        vdd_layout = QHBoxLayout()
        vdd_layout.addWidget(QLabel("VDD (Write):"))
        self.vdd_voltage = QComboBox()
        self.vdd_voltage.addItems(["Default", "3.3", "4", "4.5", "5", "5.5", "6.5"])
        vdd_layout.addWidget(self.vdd_voltage)
        vdd_layout.addStretch()
        voltage_layout.addLayout(vdd_layout)
        
        vcc_layout = QHBoxLayout()
        vcc_layout.addWidget(QLabel("VCC (Verify):"))
        self.vcc_voltage = QComboBox()
        self.vcc_voltage.addItems(["Default", "3.3", "4", "4.5", "5", "5.5", "6.5"])
        vcc_layout.addWidget(self.vcc_voltage)
        vcc_layout.addStretch()
        voltage_layout.addLayout(vcc_layout)
        
        voltage_group.setLayout(voltage_layout)
        layout.addWidget(voltage_group)
        
        # SPI settings
        spi_group = QGroupBox("SPI Settings (T48)")
        spi_layout = QHBoxLayout()
        spi_layout.addWidget(QLabel("SPI Clock (MHz):"))
        self.spi_clock = QComboBox()
        self.spi_clock.addItems(["Default", "4", "8", "15", "30"])
        spi_layout.addWidget(self.spi_clock)
        spi_layout.addStretch()
        spi_group.setLayout(spi_layout)
        layout.addWidget(spi_group)
        
        # Programming options
        prog_group = QGroupBox("Programming Options")
        prog_layout = QVBoxLayout()
        
        pulse_layout = QHBoxLayout()
        pulse_layout.addWidget(QLabel("Pulse Delay (μsec):"))
        self.pulse_delay = QSpinBox()
        self.pulse_delay.setRange(0, 65535)
        self.pulse_delay.setValue(0)
        pulse_layout.addWidget(self.pulse_delay)
        pulse_layout.addStretch()
        prog_layout.addLayout(pulse_layout)
        
        self.unprotect = QCheckBox("Unprotect before programming")
        prog_layout.addWidget(self.unprotect)
        
        self.protect = QCheckBox("Protect after programming")
        prog_layout.addWidget(self.protect)
        
        prog_group.setLayout(prog_layout)
        layout.addWidget(prog_group)
        
        # ICSP settings
        icsp_group = QGroupBox("ICSP Settings")
        icsp_layout = QVBoxLayout()
        
        self.icsp_vcc = QCheckBox("Use ICSP with VCC")
        icsp_layout.addWidget(self.icsp_vcc)
        
        self.icsp_no_vcc = QCheckBox("Use ICSP without VCC")
        icsp_layout.addWidget(self.icsp_no_vcc)
        
        icsp_group.setLayout(icsp_layout)
        layout.addWidget(icsp_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_advanced_tab(self):
        """Advanced operations tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Logic test
        logic_group = QGroupBox("Logic/RAM IC Test")
        logic_layout = QVBoxLayout()
        
        logic_info = QLabel("Test RAM and Logic ICs for proper functionality.\n"
                           "VCC voltage can be set in Configuration tab.")
        logic_layout.addWidget(logic_info)
        
        logic_buttons = QHBoxLayout()
        logic_test_btn = QPushButton("Run Logic Test")
        logic_test_btn.clicked.connect(self.logic_test)
        logic_buttons.addWidget(logic_test_btn)
        logic_buttons.addStretch()
        
        logic_layout.addLayout(logic_buttons)
        logic_group.setLayout(logic_layout)
        layout.addWidget(logic_group)
        
        # Auto-detect
        detect_group = QGroupBox("SPI Device Auto-Detection")
        detect_layout = QVBoxLayout()
        
        detect_info = QLabel("Auto-detect SPI 25xx series devices.")
        detect_layout.addWidget(detect_info)
        
        detect_opts = QHBoxLayout()
        detect_opts.addWidget(QLabel("Bus Width:"))
        self.auto_detect_width = QComboBox()
        self.auto_detect_width.addItems(["8-bit", "16-bit"])
        detect_opts.addWidget(self.auto_detect_width)
        
        auto_detect_btn = QPushButton("Auto-Detect")
        auto_detect_btn.clicked.connect(self.auto_detect)
        detect_opts.addWidget(auto_detect_btn)
        detect_opts.addStretch()
        
        detect_layout.addLayout(detect_opts)
        detect_group.setLayout(detect_layout)
        layout.addWidget(detect_group)
        
        # Custom command
        custom_group = QGroupBox("Custom Command")
        custom_layout = QVBoxLayout()
        
        custom_info = QLabel("Run custom minipro commands directly.")
        custom_layout.addWidget(custom_info)
        
        custom_cmd_layout = QHBoxLayout()
        custom_cmd_layout.addWidget(QLabel("Command:"))
        self.custom_command = QLineEdit()
        self.custom_command.setPlaceholderText("e.g., -p AT29C256@DIP28 -r output.bin")
        custom_cmd_layout.addWidget(self.custom_command)
        
        custom_layout.addLayout(custom_cmd_layout)
        
        custom_buttons = QHBoxLayout()
        custom_run_btn = QPushButton("Execute")
        custom_run_btn.clicked.connect(self.run_custom_command)
        custom_buttons.addWidget(custom_run_btn)
        custom_buttons.addStretch()
        
        custom_layout.addLayout(custom_buttons)
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    # Helper methods
    
    def browse_file(self, line_edit, save=False, filter="All Files (*)"):
        """Open file browser dialog"""
        # Get last used directory from settings
        last_dir = self.settings.value("last_directory", os.path.expanduser("~"))
        
        if save:
            filename, _ = QFileDialog.getSaveFileName(self, "Save File", last_dir, filter)
        else:
            filename, _ = QFileDialog.getOpenFileName(self, "Open File", last_dir, filter)
            
        if filename:
            line_edit.setText(filename)
            # Save the directory for next time
            self.settings.setValue("last_directory", os.path.dirname(filename))
            
    def run_command(self, command):
        """Execute a minipro command in a separate thread"""
        if self.current_thread and self.current_thread.isRunning():
            QMessageBox.warning(self, "Command Running", 
                              "A command is already running. Please wait for it to complete.")
            return
            
        self.log_console(f"$ minipro {command}\n", color="#4fc3f7")
        self.statusBar().showMessage("Running command...")
        
        # Show and reset progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")
        
        full_command = f"minipro {command}"
        self.current_thread = CommandThread(full_command, self.debug_mode.isChecked())
        self.current_thread.output_received.connect(self.log_console)
        self.current_thread.error_received.connect(lambda msg: self.log_console(msg, color="#f44336"))
        self.current_thread.progress_update.connect(self.update_progress)
        self.current_thread.debug_output.connect(lambda msg: self.log_console(msg, color="#9c27b0"))
        self.current_thread.finished_signal.connect(self.command_finished)
        self.current_thread.start()
        
    def command_finished(self, returncode):
        """Handle command completion"""
        # Hide progress bar after a short delay
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
        
        if returncode == 0:
            self.statusBar().showMessage("Command completed successfully", 3000)
            self.log_console("\n✓ Command completed successfully\n", color="#4caf50")
            self.progress_bar.setValue(100)
            self.progress_label.setText("Complete!")
        else:
            self.statusBar().showMessage(f"Command failed with code {returncode}", 5000)
            self.log_console(f"\n✗ Command failed with exit code {returncode}\n", color="#f44336")
            self.progress_label.setText("Failed")
            
    def update_progress(self, percentage, status):
        """Update progress bar and label"""
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(status)
        self.statusBar().showMessage(status)
            
    def log_console(self, message, color=None):
        """Append message to console with optional color"""
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if color:
            self.console.setTextColor(QColor(color))
        else:
            self.console.setTextColor(QColor("#d4d4d4"))
            
        self.console.append(message.rstrip())
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()
        
    def get_device_arg(self):
        """Get the device argument if specified"""
        device = self.device_combo.currentText().strip()
        if device:
            return f'-p "{device}"'
        return ""
        
    def get_memory_arg(self):
        """Get memory type argument"""
        mem_type = self.memory_type.currentText()
        if mem_type and mem_type != "code":
            return f"-c {mem_type}"
        return ""
        
    def get_format_arg(self):
        """Get file format argument"""
        format_text = self.file_format.currentText()
        if "ihex" in format_text:
            return "-f ihex"
        elif "srec" in format_text:
            return "-f srec"
        return ""
        
    def get_voltage_args(self):
        """Get voltage configuration arguments"""
        args = []
        
        if self.vpp_voltage.currentText() != "Default":
            args.append(f"--vpp {self.vpp_voltage.currentText()}")
            
        if self.vdd_voltage.currentText() != "Default":
            args.append(f"--vdd {self.vdd_voltage.currentText()}")
            
        if self.vcc_voltage.currentText() != "Default":
            args.append(f"--vcc {self.vcc_voltage.currentText()}")
            
        if self.spi_clock.currentText() != "Default":
            args.append(f"--spi_clock {self.spi_clock.currentText()}")
            
        if self.pulse_delay.value() > 0:
            args.append(f"--pulse {self.pulse_delay.value()}")
            
        return " ".join(args)
        
    def get_protection_args(self):
        """Get protection arguments"""
        args = []
        if self.unprotect.isChecked():
            args.append("-u")
        if self.protect.isChecked():
            args.append("-P")
        return " ".join(args)
        
    def get_icsp_args(self):
        """Get ICSP arguments"""
        if self.icsp_vcc.isChecked():
            return "-i"
        elif self.icsp_no_vcc.isChecked():
            return "-I"
        return ""
        
    # Command methods
    
    def detect_programmer(self):
        """Detect connected programmer"""
        self.run_command("-k")
        
    def query_supported(self):
        """Query supported programmers"""
        self.run_command("-Q")
        
    def hardware_check(self):
        """Run hardware check"""
        reply = QMessageBox.question(self, "Hardware Check",
                                     "This will run a comprehensive hardware test.\n"
                                     "Make sure no chip is inserted.\n\nContinue?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.run_command("-t")
            
    def load_device_list(self):
        """Load all supported devices into the dropdown"""
        reply = QMessageBox.question(self, "Load Device List",
                                     "This will load 13,000+ supported devices into the dropdown.\n"
                                     "This may take a few moments.\n\nContinue?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.device_combo.clear()
            self.device_combo.addItem("Loading devices...")
            self.device_combo.setEnabled(False)
            
            # Run in thread to parse output
            class DeviceListThread(QThread):
                devices_loaded = pyqtSignal(list)
                
                def run(self):
                    try:
                        result = subprocess.run(
                            ["minipro", "-l"],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        devices = []
                        in_device_list = False
                        
                        for line in result.stdout.split('\n'):
                            line = line.strip()
                            
                            # Skip header lines and empty lines
                            if not line or line.startswith('-') or line.startswith('Device'):
                                continue
                            
                            # Start capturing after we see device listings
                            if any(keyword in line.lower() for keyword in ['supported', 'device', 'name']):
                                in_device_list = True
                                continue
                            
                            # Extract device name (first column/word)
                            # Device names can have @ for package or be standalone
                            parts = line.split()
                            if parts:
                                device_name = parts[0]
                                # Filter out obvious non-device lines
                                if (device_name and 
                                    not device_name.startswith('#') and
                                    not device_name.lower() in ['note:', 'warning:', 'error:', 'found', 'total']):
                                    devices.append(device_name)
                        
                        # Remove duplicates and sort
                        devices = sorted(list(set(devices)))
                        self.devices_loaded.emit(devices)
                    except Exception as e:
                        self.devices_loaded.emit([])
            
            self.device_thread = DeviceListThread()
            self.device_thread.devices_loaded.connect(self.populate_device_list)
            self.device_thread.start()
            
    def populate_device_list(self, devices):
        """Populate the dropdown with device list"""
        self.device_combo.clear()
        self.device_combo.setEnabled(True)
        
        if devices:
            self.device_combo.addItems(sorted(devices))
            self.statusBar().showMessage(f"Loaded {len(devices)} devices", 3000)
            self.log_console(f"✓ Loaded {len(devices)} devices into dropdown\n", color="#4caf50")
        else:
            QMessageBox.warning(self, "Load Failed", 
                              "Failed to load device list. Make sure minipro is installed.")
            self.statusBar().showMessage("Failed to load devices", 3000)
            
    def get_device_info(self):
        """Get device information"""
        device = self.device_combo.currentText().strip()
        if not device:
            QMessageBox.warning(self, "Device Required", "Please select or enter a device name.")
            return
        self.run_command(f'-d "{device}"')
        
    def read_chip_id(self):
        """Read chip ID"""
        device_arg = self.get_device_arg()
        if not device_arg:
            QMessageBox.warning(self, "Device Required", "Please enter a device name.")
            return
        self.run_command(f"{device_arg} -D")
        
    def pin_check(self):
        """Check pin contacts"""
        device_arg = self.get_device_arg()
        if not device_arg:
            QMessageBox.warning(self, "Device Required", "Please enter a device name.")
            return
        self.run_command(f"{device_arg} -z")
        
    def blank_check(self):
        """Blank check device"""
        device_arg = self.get_device_arg()
        if not device_arg:
            QMessageBox.warning(self, "Device Required", "Please enter a device name.")
            return
        mem_arg = self.get_memory_arg()
        self.run_command(f"{device_arg} -b {mem_arg}".strip())
        
    def read_device(self):
        """Read from device"""
        device_arg = self.get_device_arg()
        if not device_arg:
            QMessageBox.warning(self, "Device Required", "Please enter a device name.")
            return
            
        output_file = self.read_file.text().strip()
        if not output_file:
            QMessageBox.warning(self, "File Required", "Please specify an output file.")
            return
            
        mem_arg = self.get_memory_arg()
        format_arg = self.get_format_arg()
        skip_id = "-x" if self.skip_id_check.isChecked() else ""
        
        command = f'{device_arg} -r "{output_file}" {mem_arg} {format_arg} {skip_id}'.strip()
        self.run_command(command)
        
    def write_device(self):
        """Write to device"""
        device_arg = self.get_device_arg()
        if not device_arg:
            QMessageBox.warning(self, "Device Required", "Please enter a device name.")
            return
            
        input_file = self.write_file.text().strip()
        if not input_file:
            QMessageBox.warning(self, "File Required", "Please specify an input file.")
            return
            
        if not os.path.exists(input_file):
            QMessageBox.warning(self, "File Not Found", f"File not found: {input_file}")
            return
            
        mem_arg = self.get_memory_arg()
        voltage_args = self.get_voltage_args()
        protection_args = self.get_protection_args()
        icsp_args = self.get_icsp_args()
        
        skip_erase = "-e" if self.skip_erase.isChecked() else ""
        skip_verify = "-v" if self.skip_verify.isChecked() else ""
        no_id_error = "-y" if self.no_id_error.isChecked() else ""
        no_size_error = "-s" if self.no_size_error.isChecked() else ""
        
        command = (f'{device_arg} -w "{input_file}" {mem_arg} {voltage_args} '
                  f'{protection_args} {icsp_args} {skip_erase} {skip_verify} '
                  f'{no_id_error} {no_size_error}').strip()
        
        reply = QMessageBox.question(self, "Write Device",
                                     f"Write {input_file} to device?\n\n"
                                     "This will modify the device contents.\n\nContinue?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.run_command(command)
            
    def verify_device(self):
        """Verify device contents"""
        device_arg = self.get_device_arg()
        if not device_arg:
            QMessageBox.warning(self, "Device Required", "Please enter a device name.")
            return
            
        input_file = self.write_file.text().strip()
        if not input_file:
            QMessageBox.warning(self, "File Required", "Please specify a file to verify against.")
            return
            
        if not os.path.exists(input_file):
            QMessageBox.warning(self, "File Not Found", f"File not found: {input_file}")
            return
            
        mem_arg = self.get_memory_arg()
        command = f'{device_arg} -m "{input_file}" {mem_arg}'.strip()
        self.run_command(command)
        
    def erase_device(self):
        """Erase device"""
        device_arg = self.get_device_arg()
        if not device_arg:
            QMessageBox.warning(self, "Device Required", "Please enter a device name.")
            return
            
        reply = QMessageBox.warning(self, "Erase Device",
                                    "⚠️ WARNING ⚠️\n\n"
                                    "This will permanently erase ALL data on the device!\n\n"
                                    "Are you sure you want to continue?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.run_command(f"{device_arg} -E")
            
    def update_firmware(self):
        """Update programmer firmware"""
        fw_file = self.firmware_file.text().strip()
        if not fw_file:
            QMessageBox.warning(self, "File Required", "Please specify a firmware file.")
            return
            
        if not os.path.exists(fw_file):
            QMessageBox.warning(self, "File Not Found", f"File not found: {fw_file}")
            return
            
        reply = QMessageBox.warning(self, "Update Firmware",
                                    "⚠️ FIRMWARE UPDATE ⚠️\n\n"
                                    "This will update the programmer firmware.\n"
                                    "Do NOT disconnect during the update!\n\n"
                                    "Continue?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.run_command(f'-F "{fw_file}"')
            
    def logic_test(self):
        """Run logic/RAM IC test"""
        device_arg = self.get_device_arg()
        if not device_arg:
            QMessageBox.warning(self, "Device Required", "Please enter a device name.")
            return
            
        vcc_arg = ""
        if self.vcc_voltage.currentText() != "Default":
            vcc_arg = f"--vcc {self.vcc_voltage.currentText()}"
            
        self.run_command(f"{device_arg} -T {vcc_arg}".strip())
        
    def auto_detect(self):
        """Auto-detect SPI device"""
        width = "8" if "8-bit" in self.auto_detect_width.currentText() else "16"
        self.run_command(f"-a {width}")
        
    def run_custom_command(self):
        """Run custom command"""
        command = self.custom_command.text().strip()
        if not command:
            QMessageBox.warning(self, "Command Required", "Please enter a command.")
            return
        self.run_command(command)


def main():
    # Suppress Qt platform plugin warnings
    os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)
    
    window = MiniProGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
