import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=BACKEND_ROOT / ".env")

DEFAULT_SQLITE_PATH = BACKEND_ROOT / "fastqr_local.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

# Buena práctica: leer la URL de base de datos desde el entorno. El fallback
# a SQLite permite que el proyecto funcione en local sin configuración extra,
# mientras que en producción se usa PostgreSQL vía FASTQR_DATABASE_URL.
DATABASE_URL = os.getenv("FASTQR_DATABASE_URL", DEFAULT_SQLITE_URL)
DB_CONNECT_TIMEOUT = int(os.getenv("FASTQR_DB_CONNECT_TIMEOUT", "5"))

connect_args: dict[str, object]
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {"connect_timeout": DB_CONNECT_TIMEOUT}

# pool_pre_ping=True: antes de entregar una conexión del pool, SQLAlchemy
# ejecuta un SELECT 1 para verificar que esté viva. Evita 500s cuando el
# servidor de base de datos cierra conexiones idle.
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia FastAPI que proporciona una sesión de base de datos por request.

    Por qué Generator[Session, None, None]:
    - El tipo explícito permite que FastAPI y los type checkers (mypy/pyright)
      validen que los endpoints que declaran db: Session reciben el tipo correcto.
    - El bloque finally garantiza que la sesión siempre se cierra, incluso si
      el endpoint lanza una excepción — evita leaked connections al pool.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
