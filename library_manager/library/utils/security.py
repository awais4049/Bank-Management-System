from __future__ import annotations
import hashlib
import secrets


def hash_password(plain_password: str, *, salt: str | None = None) -> str:
	if salt is None:
		salt = secrets.token_hex(16)
	pw_bytes = (salt + plain_password).encode("utf-8")
	digest = hashlib.sha256(pw_bytes).hexdigest()
	return f"sha256${salt}${digest}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
	try:
		algo, salt, digest = stored_hash.split("$")
	except ValueError:
		return False
	if algo != "sha256":
		return False
	return hash_password(plain_password, salt=salt) == stored_hash