from __future__ import annotations
from collections import Counter
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Loan, Book


class RecommendationService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def recommend_for_member(self, member_id: int, limit: int = 5) -> list[Book]:
		# Find member's past loans and favorite genres
		loaned_books = list(self.db.execute(
			select(Book.genre).join(Loan, Loan.book_id == Book.id).where(Loan.member_id == member_id)
		).scalars().all())
		genre_counts = Counter([g for g in loaned_books if g])
		preferred_genres = [g for g, _ in genre_counts.most_common(3)]
		if not preferred_genres:
			# fallback: popular available books
			return list(self.db.execute(select(Book).where(Book.available == True).limit(limit)).scalars().all())
		# Recommend available books in preferred genres not currently loaned by the member
		recommended = list(self.db.execute(
			select(Book).where(Book.available == True, Book.genre.in_(preferred_genres)).limit(limit)
		).scalars().all())
		return recommended