from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QLabel
from ...db import get_session_factory
from ...services.book_service import BookService


class BooksPage(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.current_page = 0
		self.page_size = 25
		self._setup_ui()
		self._load_data()

	def _setup_ui(self) -> None:
		layout = QVBoxLayout(self)
		search_row = QHBoxLayout()
		self.input_search = QLineEdit()
		self.input_search.setPlaceholderText("Search by title, author, ISBN")
		self.input_genre = QLineEdit()
		self.input_genre.setPlaceholderText("Genre filter")
		self.combo_avail = QComboBox()
		self.combo_avail.addItems(["All", "Available", "Unavailable"])
		self.btn_search = QPushButton("Search")
		self.btn_add = QPushButton("Add")
		self.btn_edit = QPushButton("Edit")
		self.btn_delete = QPushButton("Delete")
		search_row.addWidget(self.input_search)
		search_row.addWidget(self.input_genre)
		search_row.addWidget(self.combo_avail)
		search_row.addWidget(self.btn_search)
		search_row.addWidget(self.btn_add)
		search_row.addWidget(self.btn_edit)
		search_row.addWidget(self.btn_delete)
		layout.addLayout(search_row)
		self.table = QTableWidget(0, 6)
		self.table.setHorizontalHeaderLabels(["ID", "Title", "Author", "ISBN", "Genre", "Available"])
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
		self.btn_add.clicked.connect(self._add_stub)
		self.btn_edit.clicked.connect(self._edit_stub)
		self.btn_delete.clicked.connect(self._delete_stub)
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
		genre = self.input_genre.text().strip() or None
		avail_idx = self.combo_avail.currentIndex()
		available = None if avail_idx == 0 else (True if avail_idx == 1 else False)
		offset = self.current_page * self.page_size
		with SessionLocal() as db:
			books = BookService(db).search(query=query, genre=genre, available=available, offset=offset, limit=self.page_size)
		self.table.setRowCount(len(books))
		for row, b in enumerate(books):
			self.table.setItem(row, 0, QTableWidgetItem(str(b.id)))
			self.table.setItem(row, 1, QTableWidgetItem(b.title))
			self.table.setItem(row, 2, QTableWidgetItem(b.author))
			self.table.setItem(row, 3, QTableWidgetItem(b.isbn or ""))
			self.table.setItem(row, 4, QTableWidgetItem(b.genre or ""))
			self.table.setItem(row, 5, QTableWidgetItem("Yes" if b.available else "No"))
		self.lbl_page.setText(f"Page {self.current_page + 1}")

	def _add_stub(self) -> None:
		from PySide6.QtWidgets import QMessageBox
		QMessageBox.information(self, "Add", "Add dialog not yet implemented.")

	def _edit_stub(self) -> None:
		from PySide6.QtWidgets import QMessageBox
		QMessageBox.information(self, "Edit", "Edit dialog not yet implemented.")

	def _delete_stub(self) -> None:
		from PySide6.QtWidgets import QMessageBox
		QMessageBox.information(self, "Delete", "Delete confirmation not yet implemented.")