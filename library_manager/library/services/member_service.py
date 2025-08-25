from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Member


class MemberService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def create(self, *, name: str, email: str | None = None, phone: str | None = None) -> Member:
		member = Member(name=name, email=email, phone=phone)
		self.db.add(member)
		self.db.commit()
		self.db.refresh(member)
		return member

	def update(self, member_id: int, **kwargs) -> Member:
		member = self.db.get(Member, member_id)
		if not member:
			raise ValueError("Member not found")
		for k, v in kwargs.items():
			setattr(member, k, v)
		self.db.commit()
		self.db.refresh(member)
		return member

	def delete(self, member_id: int) -> None:
		member = self.db.get(Member, member_id)
		if not member:
			return
		self.db.delete(member)
		self.db.commit()

	def search(self, query: str = "", offset: int = 0, limit: int = 25) -> list[Member]:
		stmt = select(Member)
		if query:
			like = f"%{query}%"
			stmt = stmt.where((Member.name.ilike(like)) | (Member.email.ilike(like)))
		stmt = stmt.offset(offset).limit(limit)
		return list(self.db.execute(stmt).scalars().all())