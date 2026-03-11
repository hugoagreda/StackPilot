import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=BACKEND_ROOT / ".env")

DEFAULT_SQLITE_PATH = BACKEND_ROOT / "fastqr_local.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

DATABASE_URL = os.getenv("FASTQR_DATABASE_URL", DEFAULT_SQLITE_URL)
DB_CONNECT_TIMEOUT = int(os.getenv("FASTQR_DB_CONNECT_TIMEOUT", "5"))

connect_args: dict[str, object]
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {"connect_timeout": DB_CONNECT_TIMEOUT}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
