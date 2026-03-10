import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "FASTQR_DATABASE_URL",
    "postgresql+psycopg://fastqr:fastqr@localhost:5432/fastqr",
)
DB_CONNECT_TIMEOUT = int(os.getenv("FASTQR_DB_CONNECT_TIMEOUT", "5"))

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": DB_CONNECT_TIMEOUT},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
