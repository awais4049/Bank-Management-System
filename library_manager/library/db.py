from __future__ import annotations
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import DB_PATH, DATA_DIR, EBOOKS_DIR, BACKUP_DIR


class Base(DeclarativeBase):
	pass


_engine = None
_SessionLocal = None


def get_engine():
	global _engine
	if _engine is None:
		DATA_DIR.mkdir(parents=True, exist_ok=True)
		EBOOKS_DIR.mkdir(parents=True, exist_ok=True)
		BACKUP_DIR.mkdir(parents=True, exist_ok=True)
		conn_str = f"sqlite:///{DB_PATH}"
		_engine = create_engine(conn_str, echo=False, future=True)
	return _engine


def get_session_factory():
	global _SessionLocal
	if _SessionLocal is None:
		_SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)
	return _SessionLocal


def init_db(models_module) -> None:
	engine = get_engine()
	models_module.Base.metadata.create_all(bind=engine)