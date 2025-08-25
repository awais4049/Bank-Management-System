from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QInputDialog, QMessageBox
from ...db import get_session_factory
from sqlalchemy import select
from ...models import Member
from ...services.member_service import MemberService


class MembersPage(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.current_page = 0
		self.page_size = 25
		self._setup_ui()
		self._load_data()

	def _setup_ui(self) -> None:
		layout = QVBoxLayout(self)
		row = QHBoxLayout()
		self.input_search = QLineEdit()
		self.input_search.setPlaceholderText("Search by name or email")
		self.btn_search = QPushButton("Search")
		self.btn_add = QPushButton("Add")
		self.btn_edit = QPushButton("Edit")
		self.btn_delete = QPushButton("Delete")
		row.addWidget(self.input_search)
		row.addWidget(self.btn_search)
		row.addWidget(self.btn_add)
		row.addWidget(self.btn_edit)
		row.addWidget(self.btn_delete)
		layout.addLayout(row)
		self.table = QTableWidget(0, 5)
		self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "Active"])
		self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		layout.addWidget(self.table)
		pager_row = QHBoxLayout()
		self.btn_prev = QPushButton("Prev")
		self.btn_next = QPushButton("Next")
		self.lbl_page = QLabel("Page 1")
		pager_row.addWidget(self.btn_prev)
		pager_row.addWidget(self.btn_next)
		pager_row.addWidget(self.lbl_page)
		pager_row.addStretch()
		layout.addLayout(pager_row)
		self.btn_search.clicked.connect(self._reset_and_load)
		self.btn_add.clicked.connect(self._add)
		self.btn_edit.clicked.connect(self._edit)
		self.btn_delete.clicked.connect(self._delete)
		self.btn_prev.clicked.connect(self._prev_page)
		self.btn_next.clicked.connect(self._next_page)

	def _reset_and_load(self) -> None:
		self.current_page = 0
		self._load_data()

	def _next_page(self) -> None:
		self.current_page += 1
		self._load_data()

	def _prev_page(self) -> None:
		if self.current_page > 0:
			self.current_page -= 1
			self._load_data()

	def _load_data(self) -> None:
		SessionLocal = get_session_factory()
		query = self.input_search.text().strip()
		offset = self.current_page * self.page_size
		with SessionLocal() as db:
			members = MemberService(db).search(query=query, offset=offset, limit=self.page_size)
		self.table.setRowCount(len(members))
		for row, m in enumerate(members):
			self.table.setItem(row, 0, QTableWidgetItem(str(m.id)))
			self.table.setItem(row, 1, QTableWidgetItem(m.name))
			self.table.setItem(row, 2, QTableWidgetItem(m.email or ""))
			self.table.setItem(row, 3, QTableWidgetItem(m.phone or ""))
			self.table.setItem(row, 4, QTableWidgetItem("Yes" if m.active else "No"))
		self.lbl_page.setText(f"Page {self.current_page + 1}")

	def _selected_member_id(self) -> int | None:
		row = self.table.currentRow()
		if row < 0:
			return None
		item = self.table.item(row, 0)
		return int(item.text()) if item else None

	def _add(self) -> None:
		name, ok = QInputDialog.getText(self, "Add Member", "Name:")
		if not ok or not name.strip():
			return
		email, _ = QInputDialog.getText(self, "Add Member", "Email (optional):")
		phone, _ = QInputDialog.getText(self, "Add Member", "Phone (optional):")
		SessionLocal = get_session_factory()
		with SessionLocal() as db:
			MemberService(db).create(name=name.strip(), email=email.strip() or None, phone=phone.strip() or None)
		self._reset_and_load()

	def _edit(self) -> None:
		member_id = self._selected_member_id()
		if not member_id:
			QMessageBox.information(self, "Edit", "Select a member row first")
			return
		name, ok = QInputDialog.getText(self, "Edit Member", "Name:")
		if not ok:
			return
		email, _ = QInputDialog.getText(self, "Edit Member", "Email:")
		phone, _ = QInputDialog.getText(self, "Edit Member", "Phone:")
		SessionLocal = get_session_factory()
		with SessionLocal() as db:
			MemberService(db).update(member_id, name=name or None, email=email or None, phone=phone or None)
		self._load_data()

	def _delete(self) -> None:
		member_id = self._selected_member_id()
		if not member_id:
			QMessageBox.information(self, "Delete", "Select a member row first")
			return
		SessionLocal = get_session_factory()
		with SessionLocal() as db:
			MemberService(db).delete(member_id)
		self._reset_and_load()