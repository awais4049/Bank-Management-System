from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from ...db import get_session_factory
from ...services.loan_service import LoanService


class LoansPage(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self._setup_ui()

	def _setup_ui(self) -> None:
		layout = QVBoxLayout(self)
		row = QHBoxLayout()
		self.input_book_id = QLineEdit()
		self.input_book_id.setPlaceholderText("Book ID")
		self.input_member_id = QLineEdit()
		self.input_member_id.setPlaceholderText("Member ID")
		self.btn_issue = QPushButton("Issue Book")
		self.input_loan_id = QLineEdit()
		self.input_loan_id.setPlaceholderText("Loan ID")
		self.btn_return = QPushButton("Return Book")
		row.addWidget(QLabel("Issue:"))
		row.addWidget(self.input_book_id)
		row.addWidget(self.input_member_id)
		row.addWidget(self.btn_issue)
		row2 = QHBoxLayout()
		row2.addWidget(QLabel("Return:"))
		row2.addWidget(self.input_loan_id)
		row2.addWidget(self.btn_return)
		layout.addLayout(row)
		layout.addLayout(row2)
		self.btn_issue.clicked.connect(self._issue)
		self.btn_return.clicked.connect(self._return)

	def _issue(self) -> None:
		SessionLocal = get_session_factory()
		try:
			book_id = int(self.input_book_id.text())
			member_id = int(self.input_member_id.text())
		except ValueError:
			QMessageBox.warning(self, "Issue", "Enter valid numeric IDs")
			return
		with SessionLocal() as db:
			service = LoanService(db)
			try:
				loan = service.issue_book(book_id, member_id)
				QMessageBox.information(self, "Issued", f"Loan created with ID {loan.id}")
			except Exception as exc:
				QMessageBox.critical(self, "Issue Failed", str(exc))

	def _return(self) -> None:
		SessionLocal = get_session_factory()
		try:
			loan_id = int(self.input_loan_id.text())
		except ValueError:
			QMessageBox.warning(self, "Return", "Enter valid numeric loan ID")
			return
		with SessionLocal() as db:
			service = LoanService(db)
			try:
				loan = service.return_book(loan_id)
				if loan.fine_paid > 0:
					QMessageBox.information(self, "Returned", f"Book returned. Fine due: {loan.fine_paid:.2f}")
				else:
					QMessageBox.information(self, "Returned", "Book returned on time.")
			except Exception as exc:
				QMessageBox.critical(self, "Return Failed", str(exc))