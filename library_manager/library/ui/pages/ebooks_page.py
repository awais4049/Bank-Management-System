from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QListWidget, QMessageBox
from PySide6.QtCore import Qt
try:
	from PySide6.QtPdf import QPdfDocument
	from PySide6.QtPdfWidgets import QPdfView
except Exception:  # pragma: no cover - optional module
	QPdfDocument = None
	QPdfView = None
from ...db import get_session_factory
from ...models import Book
from sqlalchemy import select


class EBooksPage(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		layout = QVBoxLayout(self)
		rows = QHBoxLayout()
		self.btn_attach = QPushButton("Attach PDF to Book ID…")
		self.btn_refresh = QPushButton("Refresh List")
		rows.addWidget(self.btn_attach)
		rows.addWidget(self.btn_refresh)
		layout.addLayout(rows)
		self.list = QListWidget()
		layout.addWidget(self.list)
		self.viewer = None
		if QPdfDocument and QPdfView:
			self._doc = QPdfDocument(self)
			self.viewer = QPdfView(self)
			self.viewer.setDocument(self._doc)
			layout.addWidget(self.viewer)
		else:
			layout.addWidget(QPushButton("PDF Viewer not available (QtPdf missing)"))
		self.btn_attach.clicked.connect(self._attach_pdf)
		self.btn_refresh.clicked.connect(self._refresh)
		self._refresh()

	def _refresh(self) -> None:
		SessionLocal = get_session_factory()
		with SessionLocal() as db:
			rows = list(db.execute(select(Book).where(Book.file_path.is_not(None))).scalars().all())
		self.list.clear()
		for b in rows:
			self.list.addItem(f"{b.id}: {b.title} — {Path(b.file_path).name}")
		self.list.itemSelectionChanged.connect(self._open_selected)

	def _open_selected(self) -> None:
		if not self.viewer:
			return
		text = self.list.currentItem().text() if self.list.currentItem() else ""
		if not text:
			return
		book_id = int(text.split(":", 1)[0])
		SessionLocal = get_session_factory()
		with SessionLocal() as db:
			book = db.get(Book, book_id)
			if book and book.file_path and Path(book.file_path).exists():
				self.viewer.document().load(book.file_path)
			else:
				QMessageBox.warning(self, "Open PDF", "File not found.")

	def _attach_pdf(self) -> None:
		file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
		if not file_path:
			return
		# Ask for book ID
		from PySide6.QtWidgets import QInputDialog
		book_id, ok = QInputDialog.getInt(self, "Attach PDF", "Enter Book ID:")
		if not ok:
			return
		SessionLocal = get_session_factory()
		with SessionLocal() as db:
			book = db.get(Book, int(book_id))
			if not book:
				QMessageBox.warning(self, "Attach PDF", "Book not found.")
				return
			book.file_path = file_path
			db.commit()
			QMessageBox.information(self, "Attach PDF", "PDF attached to book.")
		self._refresh()