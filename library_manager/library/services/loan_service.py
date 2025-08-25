from __future__ import annotations
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Loan, Book, Member
from ..config import LOAN_DAYS_DEFAULT, FINE_PER_DAY


class LoanService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def issue_book(self, book_id: int, member_id: int) -> Loan:
		book = self.db.get(Book, book_id)
		member = self.db.get(Member, member_id)
		if not book or not member:
			raise ValueError("Invalid book or member")
		if not book.available:
			raise ValueError("Book not available")
		issued_on = date.today()
		due_on = issued_on + timedelta(days=LOAN_DAYS_DEFAULT)
		loan = Loan(book_id=book_id, member_id=member_id, issued_on=issued_on, due_on=due_on)
		book.available = False
		self.db.add(loan)
		self.db.commit()
		self.db.refresh(loan)
		return loan

	def return_book(self, loan_id: int) -> Loan:
		loan = self.db.get(Loan, loan_id)
		if not loan or loan.returned_on is not None:
			raise ValueError("Invalid or already returned loan")
		loan.returned_on = date.today()
		# Calculate fines
		if loan.returned_on > loan.due_on:
			days_late = (loan.returned_on - loan.due_on).days
			loan.fine_paid = float(days_late * FINE_PER_DAY)
		book = self.db.get(Book, loan.book_id)
		if book:
			book.available = True
		self.db.commit()
		self.db.refresh(loan)
		return loan