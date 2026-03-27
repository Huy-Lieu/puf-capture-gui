import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QComboBox,
                             QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QFileDialog)
import time
from PyQt6.QtCore import QThread, pyqtSignal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_conn = None
        self.output_file = None

        self.setWindowTitle("PUF Binary Capture Tool (Qt6)")
        self.setGeometry(100, 100, 400, 300)

        # --- UI LAYOUT ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. COM Port Selection
        hbox_com = QHBoxLayout()
        self.com_label = QLabel("COM Port:")
        self.com_combo = QComboBox()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_com_ports)
        hbox_com.addWidget(self.com_label)
        hbox_com.addWidget(self.com_combo)
        hbox_com.addWidget(self.refresh_btn)
        main_layout.addLayout(hbox_com)

        # 2. Baud Rate Selection
        hbox_baud = QHBoxLayout()
        self.baud_label = QLabel("Baud Rate:")
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600","115200"])
        self.baud_combo.setCurrentText("115200")  # Default
        hbox_baud.addWidget(self.baud_label)
        hbox_baud.addWidget(self.baud_combo)
        main_layout.addLayout(hbox_baud)

        # 3. Connection Buttons
        hbox_conn = QHBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_to_fpga)
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_from_fpga)
        self.disconnect_btn.setEnabled(False)
        hbox_conn.addWidget(self.connect_btn)
        hbox_conn.addWidget(self.disconnect_btn)
        main_layout.addLayout(hbox_conn)


        # Added File Section
        hbox_file = QHBoxLayout()
        self.file_label = QLabel("Output File:")
        self.file_path_display = QLabel("No file selected") # Using Label instead of Edit for safety
        self.file_path_display.setStyleSheet("border: 1px solid gray; padding: 2px;")
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.select_file) # Logic to be added later

        hbox_file.addWidget(self.file_label)
        hbox_file.addWidget(self.file_path_display)
        hbox_file.addWidget(self.browse_btn)
        main_layout.addLayout(hbox_file)

        # Added Capture Control
        hbox_capture = QHBoxLayout()
        self.start_btn = QPushButton("Capture")
        self.start_btn.setEnabled(False)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)

        hbox_capture.addWidget(self.start_btn)
        hbox_capture.addWidget(self.stop_btn)
        main_layout.addLayout(hbox_capture)

        # 5. Status Label
        self.status_label = QLabel("Status: Disconnected")
        main_layout.addWidget(self.status_label)

        # Initialize ports
        self.refresh_com_ports()

    # --- LOGIC ---

    def refresh_com_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_combo.clear()
        self.com_combo.addItems(ports if ports else ["No ports found"])

    def connect_to_fpga(self):
        baud = int(self.baud_combo.currentText())
        com = self.com_combo.currentText()
        try:
            # timeout=0 makes read() non-blocking
            self.serial_conn = serial.Serial(com, baud, timeout=0)
            self.serial_conn.reset_input_buffer()

            self.status_label.setText(f"Status: Connected to {com}")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.start_btn.setEnabled(True)
            self.com_combo.setEnabled(False)
            self.baud_combo.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))

    def disconnect_from_fpga(self):
        if self.serial_conn and self.serial_conn.is_open:
            # self.stop_capture()  # Ensure we stop before closing
            self.serial_conn.close()
        self.serial_conn = None

        self.status_label.setText("Status: Disconnected")
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.com_combo.setEnabled(True)
        self.baud_combo.setEnabled(True)

    def select_file(self):
        # Open a "Save As" dialog
        # Returns a tuple: (filename, filter_used)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Capture As",
            "",
            "Binary Files (*.bin, *.txt);;All Files (*)"
        )

        if file_path:
            self.output_file = file_path
            self.file_path_display.setText(file_path)
            # Optional: Print to console for debugging
            print(f"File selected: {self.output_file}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())