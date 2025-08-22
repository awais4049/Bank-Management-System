from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class DashboardPage(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		layout = QVBoxLayout(self)
		layout.addWidget(QLabel("Dashboard - Borrowing trends and stats will appear here."))