from __future__ import annotations
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Loan, Book, Member


class NotificationService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def get_due_soon(self, within_days: int = 1) -> list[tuple[Loan, Book, Member]]:
		today = date.today()
		limit_date = today + timedelta(days=within_days)
		stmt = (
			select(Loan, Book, Member)
			.join(Book, Loan.book_id == Book.id)
			.join(Member, Loan.member_id == Member.id)
			.where(Loan.returned_on.is_(None), Loan.due_on <= limit_date, Loan.due_on >= today)
		)
		return list(self.db.execute(stmt).all())

	def get_overdue(self) -> list[tuple[Loan, Book, Member]]:
		today = date.today()
		stmt = (
			select(Loan, Book, Member)
			.join(Book, Loan.book_id == Book.id)
			.join(Member, Loan.member_id == Member.id)
			.where(Loan.returned_on.is_(None), Loan.due_on < today)
		)
		return list(self.db.execute(stmt).all())