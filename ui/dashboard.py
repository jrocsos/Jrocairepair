# ui/dashboard.py
import sys
import logging
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, 
                             QTextEdit, QLabel, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Import our core engine
from core.engine import UniversalUnlockEngine

logger = logging.getLogger(__name__)

class DashboardWindow(QMainWindow):
    def __init__(self, engine: UniversalUnlockEngine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("OmniKey Master - Universal Unlocker")
        self.setGeometry(100, 100, 1000, 700)
        
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_devices)
        self.timer.start(5000) # Refresh every 5 seconds
        
        # Initial scan simulation
        self.simulate_scan()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("OmniKey Master")
        self.lbl_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        self.lbl_status = QLabel("Status: Online")
        header_layout.addWidget(self.lbl_status)
        layout.addLayout(header_layout)

        # Device Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Serial", "Model", "OS/Lock", "Connection", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Log Console
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFont(QFont("Courier New", 10))
        layout.addWidget(self.log_box, 1) # Weight 1 to expand

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Devices")
        self.btn_refresh.clicked.connect(self.refresh_devices)
        self.btn_unlock = QPushButton("Master Unlock Selected")
        self.btn_unlock.clicked.connect(self.master_unlock_selected)
        self.btn_unlock.setEnabled(False)
        
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_unlock)
        layout.addLayout(btn_layout)

        # Connect table selection change
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

    def simulate_scan(self):
        """Simulate detecting some devices for demo purposes."""
        # In real app, this scans USB/Network
        pass

    def refresh_devices(self):
        self.table.setRowCount(0)
        devices = self.engine.device_manager.get_all_devices()
        
        for dev in devices:
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            
            info = dev.get_device_info()
            self.table.setItem(row_pos, 0, QTableWidgetItem(dev.serial))
            self.table.setItem(row_pos, 1, QTableWidgetItem(info.get('model', 'Unknown')))
            self.table.setItem(row_pos, 2, QTableWidgetItem(f"{info.get('os_version', 'N/A')} / {info.get('lock_type', 'N/A')}"))
            self.table.setItem(row_pos, 3, QTableWidgetItem(info.get('connection', 'N/A')))
            
            # Action Button
            btn = QPushButton("Unlock")
            btn.clicked.connect(lambda checked, s=dev.serial: self.trigger_unlock(s))
            self.table.setCellWidget(row_pos, 4, btn)

    def on_selection_changed(self):
        rows = self.table.selectedItems()
        self.btn_unlock.setEnabled(len(rows) > 0)

    def master_unlock_selected(self):
        rows = self.table.selectedItems()
        if rows:
            serial = rows[0].text()
            self.trigger_unlock(serial)

    def trigger_unlock(self, serial: str):
        self.log(f"Starting Master Unlock for {serial}...")
        result = self.engine.master_unlock(serial)
        
        logs = result.get('result', {}).get('logs', [])
        for log in logs:
            self.log(log)
            
        if result.get('success'):
            self.log(f"✅ Success: {result.get('result', {}).get('method', 'unknown')}")
            QMessageBox.information(self, "Success", f"Device {serial} unlocked successfully!")
        else:
            self.log(f"❌ Failed: {result.get('result', {}).get('logs', ['No logs'])}")
            QMessageBox.warning(self, "Failure", "Unlock failed. Check logs.")

    def log(self, message: str):
        self.log_box.append(f"[{self.current_time()}] {message}")

    def current_time(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
