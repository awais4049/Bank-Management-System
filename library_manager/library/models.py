from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Date, DateTime, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class User(Base):
	__tablename__ = "users"
	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
	password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
	role: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # Admin, Librarian, Member
	full_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Member(Base):
	__tablename__ = "members"
	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(128), nullable=False)
	email: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
	phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	loans: Mapped[list["Loan"]] = relationship(back_populates="member")


class Category(Base):
	__tablename__ = "categories"
	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
	books: Mapped[list["Book"]] = relationship(back_populates="category")


class Book(Base):
	__tablename__ = "books"
	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	title: Mapped[str] = mapped_column(String(256), index=True)
	author: Mapped[str] = mapped_column(String(128), index=True)
	isbn: Mapped[Optional[str]] = mapped_column(String(32), unique=True, index=True)
	genre: Mapped[Optional[str]] = mapped_column(String(64), index=True)
	category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
	available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
	file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)  # optional PDF/e-book path
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	category: Mapped[Optional[Category]] = relationship(back_populates="books")
	loans: Mapped[list["Loan"]] = relationship(back_populates="book")

	__table_args__ = (
		UniqueConstraint("title", "author", name="uq_book_title_author"),
	)


class Loan(Base):
	__tablename__ = "loans"
	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False, index=True)
	member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False, index=True)
	issued_on: Mapped[date] = mapped_column(Date, nullable=False)
	due_on: Mapped[date] = mapped_column(Date, nullable=False)
	returned_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
	fine_paid: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

	book: Mapped[Book] = relationship(back_populates="loans")
	member: Mapped[Member] = relationship(back_populates="loans")