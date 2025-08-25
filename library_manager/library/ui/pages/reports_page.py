from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ...db import get_session_factory
from ...models import Loan, Book
from sqlalchemy import select, func


class ReportsPage(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self._figure = Figure(figsize=(5, 3))
		self._canvas = FigureCanvas(self._figure)
		layout = QVBoxLayout(self)
		layout.addWidget(QLabel("Reports & Analytics"))
		layout.addWidget(self._canvas)
		self.btn_refresh = QPushButton("Refresh")
		self.btn_refresh.clicked.connect(self._refresh)
		layout.addWidget(self.btn_refresh, alignment=Qt.AlignLeft)
		self._refresh()

	def _refresh(self) -> None:
		# Plot top 5 most borrowed books
		SessionLocal = get_session_factory()
		with SessionLocal() as db:
			stmt = (
				select(Book.title, func.count(Loan.id).label("cnt"))
				.join(Loan, Loan.book_id == Book.id)
				.group_by(Book.id)
				.order_by(func.count(Loan.id).desc())
				.limit(5)
			)
			rows = list(db.execute(stmt).all())
		ax = self._figure.subplots()
		ax.clear()
		if rows:
			titles = [r[0] for r in rows]
			counts = [r[1] for r in rows]
			ax.barh(titles, counts)
			ax.invert_yaxis()
			ax.set_title("Top 5 Books")
			ax.set_xlabel("Borrow count")
		else:
			ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
		self._canvas.draw_idle()