import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=BACKEND_ROOT / ".env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("FASTQR_JWT_SECRET", "change-me-fastqr-dev-secret")
JWT_ALGORITHM = os.getenv("FASTQR_JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("FASTQR_JWT_EXPIRE_MINUTES", "480"))


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(payload: dict, expires_minutes: int | None = None) -> str:
    expire_delta = timedelta(minutes=expires_minutes or JWT_EXPIRE_MINUTES)
    expire_at = datetime.now(timezone.utc) + expire_delta
    token_payload = {**payload, "exp": expire_at}
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
