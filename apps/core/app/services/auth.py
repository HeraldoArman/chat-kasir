"""Authentication services: JWT + password hashing with scrypt."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_config

pwd_context = CryptContext(schemes=["scrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    config = get_config()
    expire = datetime.now(UTC) + (expires_delta or timedelta(hours=24))
    to_encode = {"sub": str(subject), "exp": expire, "type": "access"}
    return jwt.encode(to_encode, config.jwt.secret_key, algorithm=config.jwt.algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    config = get_config()
    try:
        payload = jwt.decode(
            token,
            config.jwt.secret_key,
            algorithms=[config.jwt.algorithm],
            options={"verify_exp": True},
        )
        return payload
    except JWTError:
        return None
