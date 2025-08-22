from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import User
from ..utils.security import hash_password, verify_password
from ..config import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD


class AuthService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def ensure_default_admin(self) -> None:
		user = self.db.execute(select(User).where(User.username == DEFAULT_ADMIN_USERNAME)).scalar_one_or_none()
		if user is None:
			user = User(
				username=DEFAULT_ADMIN_USERNAME,
				password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
				role="Admin",
				full_name="Administrator",
				active=True,
			)
			self.db.add(user)
			self.db.commit()

	def authenticate(self, username: str, password: str) -> User | None:
		user = self.db.execute(select(User).where(User.username == username, User.active == True)).scalar_one_or_none()
		if user and verify_password(password, user.password_hash):
			return user
		return None