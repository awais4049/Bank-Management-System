from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Book


class BookService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def create(self, **kwargs) -> Book:
		book = Book(**kwargs)
		self.db.add(book)
		self.db.commit()
		self.db.refresh(book)
		return book

	def update(self, book_id: int, **kwargs) -> Book:
		book = self.db.get(Book, book_id)
		if not book:
			raise ValueError("Book not found")
		for k, v in kwargs.items():
			setattr(book, k, v)
		self.db.commit()
		self.db.refresh(book)
		return book

	def delete(self, book_id: int) -> None:
		book = self.db.get(Book, book_id)
		if not book:
			return
		self.db.delete(book)
		self.db.commit()

	def search(self, query: str = "", genre: str | None = None, available: bool | None = None, offset: int = 0, limit: int = 25) -> list[Book]:
		stmt = select(Book)
		if query:
			like = f"%{query}%"
			stmt = stmt.where((Book.title.ilike(like)) | (Book.author.ilike(like)) | (Book.isbn.ilike(like)))
		if genre:
			stmt = stmt.where(Book.genre == genre)
		if available is not None:
			stmt = stmt.where(Book.available == available)
		stmt = stmt.offset(offset).limit(limit)
		return list(self.db.execute(stmt).scalars().all())