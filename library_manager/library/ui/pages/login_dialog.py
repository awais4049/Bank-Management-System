from __future__ import annotations
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QHBoxLayout


class LoginDialog(QDialog):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Login")
		layout = QVBoxLayout(self)
		self.input_username = QLineEdit()
		self.input_username.setPlaceholderText("Username")
		self.input_password = QLineEdit()
		self.input_password.setPlaceholderText("Password")
		self.input_password.setEchoMode(QLineEdit.Password)
		layout.addWidget(QLabel("Username"))
		layout.addWidget(self.input_username)
		layout.addWidget(QLabel("Password"))
		layout.addWidget(self.input_password)
		btn_row = QHBoxLayout()
		self.btn_login = QPushButton("Login")
		self.btn_cancel = QPushButton("Cancel")
		btn_row.addWidget(self.btn_login)
		btn_row.addWidget(self.btn_cancel)
		layout.addLayout(btn_row)
		self.btn_login.clicked.connect(self.accept)
		self.btn_cancel.clicked.connect(self.reject)

	def get_credentials(self) -> tuple[str, str]:
		return self.input_username.text().strip(), self.input_password.text()