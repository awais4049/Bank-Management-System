from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QMessageBox
from PySide6.QtCore import Qt
import cv2


class ScannerPage(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		layout = QVBoxLayout(self)
		self.btn_open = QPushButton("Open Image to Scan QR")
		self.lbl_result = QLabel("No scan yet")
		self.lbl_result.setWordWrap(True)
		layout.addWidget(self.btn_open)
		layout.addWidget(self.lbl_result)
		self.btn_open.clicked.connect(self._open_and_scan)

	def _open_and_scan(self) -> None:
		file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
		if not file_path:
			return
		img = cv2.imread(file_path)
		if img is None:
			QMessageBox.warning(self, "Scan", "Failed to load image")
			return
		detector = cv2.QRCodeDetector()
		data, points, _ = detector.detectAndDecode(img)
		if data:
			self.lbl_result.setText(f"Detected QR: {data}")
		else:
			self.lbl_result.setText("No QR code detected")