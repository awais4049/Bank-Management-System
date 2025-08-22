from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QMessageBox
from ...db import get_session_factory
from ...services.recommendation_service import RecommendationService


class RecommendationsPage(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		layout = QVBoxLayout(self)
		row = QHBoxLayout()
		self.input_member_id = QLineEdit()
		self.input_member_id.setPlaceholderText("Member ID")
		self.btn_refresh = QPushButton("Recommend")
		row.addWidget(self.input_member_id)
		row.addWidget(self.btn_refresh)
		layout.addLayout(row)
		self.list = QListWidget()
		layout.addWidget(self.list)
		self.btn_refresh.clicked.connect(self._refresh)

	def _refresh(self) -> None:
		try:
			member_id = int(self.input_member_id.text())
		except ValueError:
			QMessageBox.warning(self, "Recommend", "Enter a valid member ID")
			return
		SessionLocal = get_session_factory()
		with SessionLocal() as db:
			recs = RecommendationService(db).recommend_for_member(member_id, limit=10)
		self.list.clear()
		for b in recs:
			self.list.addItem(f"{b.title} — {b.author} ({b.genre or 'N/A'})")