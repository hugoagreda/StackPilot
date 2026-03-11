import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# pool_pre_ping=True: antes de entregar una conexión del pool, SQLAlchemy
# ejecuta un SELECT 1 para verificar que esté viva. Evita 500s cuando el
# servidor de base de datos cierra conexiones idle.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
