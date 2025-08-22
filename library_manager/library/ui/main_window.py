from __future__ import annotations
import os
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
	QMainWindow,
	QWidget,
	QVBoxLayout,
	QStackedWidget,
	QToolBar,
	QStatusBar,
	QDockWidget,
	QListWidget,
	QListWidgetItem,
	QMessageBox,
	QFileDialog,
)

from ..db import get_session_factory, init_db
from .. import models
from ..services.auth_service import AuthService
from .pages.login_dialog import LoginDialog
from .pages.dashboard_page import DashboardPage
from .pages.books_page import BooksPage
from .pages.members_page import MembersPage
from .pages.loans_page import LoansPage
from .pages.reports_page import ReportsPage
from .pages.ebooks_page import EBooksPage
from .pages.recommendations_page import RecommendationsPage
from .pages.scanner_page import ScannerPage
from ..config import APP_NAME, LIGHT_THEME, DARK_THEME


class MainWindow(QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		self.setWindowTitle(APP_NAME)
		self.setMinimumSize(QSize(1100, 720))

		# Database init and default admin
		SessionLocal = get_session_factory()
		init_db(models)
		with SessionLocal() as db:
			AuthService(db).ensure_default_admin()

		self._build_ui()
		self._apply_light_theme()
		self._do_login()

	def _build_ui(self) -> None:
		central = QWidget()
		central_layout = QVBoxLayout(central)
		self.stack = QStackedWidget()
		central_layout.addWidget(self.stack)
		self.setCentralWidget(central)

		# Pages
		self.dashboard_page = DashboardPage(self)
		self.books_page = BooksPage(self)
		self.members_page = MembersPage(self)
		self.loans_page = LoansPage(self)
		self.reports_page = ReportsPage(self)
		self.ebooks_page = EBooksPage(self)
		self.reco_page = RecommendationsPage(self)
		self.scanner_page = ScannerPage(self)

		self.stack.addWidget(self.dashboard_page)
		self.stack.addWidget(self.books_page)
		self.stack.addWidget(self.members_page)
		self.stack.addWidget(self.loans_page)
		self.stack.addWidget(self.reports_page)
		self.stack.addWidget(self.ebooks_page)
		self.stack.addWidget(self.reco_page)
		self.stack.addWidget(self.scanner_page)

		# Sidebar
		self._build_sidebar()
		# Toolbar
		self._build_toolbar()
		# Status
		self.setStatusBar(QStatusBar())

	def _build_sidebar(self) -> None:
		dock = QDockWidget("Navigation", self)
		dock.setAllowedAreas(Qt.LeftDockWidgetArea)
		self.addDockWidget(Qt.LeftDockWidgetArea, dock)
		self.nav_list = QListWidget()
		for text in ["Dashboard", "Books", "Members", "Loans", "Reports", "E-Books", "Recommendations", "Scanner"]:
			item = QListWidgetItem(text)
			self.nav_list.addItem(item)
		self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
		self.nav_list.setCurrentRow(0)
		dock.setWidget(self.nav_list)

	def _build_toolbar(self) -> None:
		toolbar = QToolBar("Main")
		toolbar.setIconSize(QSize(18, 18))
		self.addToolBar(toolbar)

		# Theme toggle
		self.action_toggle_theme = QAction("Toggle Theme", self)
		self.action_toggle_theme.triggered.connect(self._toggle_theme)
		toolbar.addAction(self.action_toggle_theme)

		# Backup/Restore (stubs)
		self.action_backup = QAction("Backup DB", self)
		self.action_backup.triggered.connect(self._backup_db)
		self.action_restore = QAction("Restore DB", self)
		self.action_restore.triggered.connect(self._restore_db)
		toolbar.addAction(self.action_backup)
		toolbar.addAction(self.action_restore)

		# Logout
		self.action_logout = QAction("Logout", self)
		self.action_logout.triggered.connect(self._do_login)
		toolbar.addAction(self.action_logout)

	def _apply_light_theme(self) -> None:
		self.setStyleSheet("")

	def _apply_dark_theme(self) -> None:
		# Simple dark palette via stylesheet
		self.setStyleSheet(
			"""
			QWidget { background: #121212; color: #e0e0e0; }
			QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTableView { background: #1e1e1e; color: #e0e0e0; border: 1px solid #333; }
			QPushButton { background: #2a2a2a; border: 1px solid #444; padding: 6px 10px; }
			QPushButton:hover { background: #333333; }
			QHeaderView::section { background: #1e1e1e; color: #e0e0e0; }
			QToolBar { background: #1a1a1a; }
			QStatusBar { background: #1a1a1a; }
			"""
		)

	def _toggle_theme(self) -> None:
		if self.styleSheet():
			self._apply_light_theme()
		else:
			self._apply_dark_theme()

	def _do_login(self) -> None:
		SessionLocal = get_session_factory()
		while True:
			dialog = LoginDialog(self)
			if dialog.exec() == dialog.Accepted:
				username, password = dialog.get_credentials()
				with SessionLocal() as db:
					user = AuthService(db).authenticate(username, password)
					if user:
						self.statusBar().showMessage(f"Logged in as {user.username} ({user.role})")
						break
					else:
						QMessageBox.warning(self, "Login Failed", "Invalid username or password")
			else:
				os._exit(0)

	def _backup_db(self) -> None:
		from ..config import DB_PATH, BACKUP_DIR
		BACKUP_DIR.mkdir(parents=True, exist_ok=True)
		file_path, _ = QFileDialog.getSaveFileName(self, "Save Database Backup", str(BACKUP_DIR / "library_backup.sqlite"), "SQLite Files (*.sqlite *.db)")
		if file_path:
			try:
				import shutil
				shutil.copy2(DB_PATH, file_path)
				QMessageBox.information(self, "Backup", "Database backup saved.")
			except Exception as exc:
				QMessageBox.critical(self, "Backup Failed", str(exc))

	def _restore_db(self) -> None:
		from ..config import DB_PATH
		file_path, _ = QFileDialog.getOpenFileName(self, "Select Database Backup", "", "SQLite Files (*.sqlite *.db)")
		if file_path:
			try:
				import shutil
				shutil.copy2(file_path, DB_PATH)
				QMessageBox.information(self, "Restore", "Database restored. Restart app to apply.")
			except Exception as exc:
				QMessageBox.critical(self, "Restore Failed", str(exc))