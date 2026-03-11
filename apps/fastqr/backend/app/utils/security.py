"""
app/utils/security.py — Primitivas de seguridad: JWT y hashing de contraseñas.

Este módulo NO contiene lógica de negocio. Solo operaciones criptográficas
reutilizables de bajo nivel, para que los servicios no dependan directamente
de python-jose ni de passlib.
"""
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=BACKEND_ROOT / ".env")

# Bcrypt es el algoritmo recomendado para hashing de contraseñas porque:
# - Es lento por diseño (coste adaptable): dificulta ataques de fuerza bruta.
# - Incluye salt automático: dos hashes de la misma contraseña son distintos.
# deprecated="auto" migra automáticamente hashes de algoritmos anteriores.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# Configuración JWT — fail-fast en arranque si falta el secreto
# ---------------------------------------------------------------------------
# Buena práctica: si FASTQR_JWT_SECRET no está definida, lanzar RuntimeError
# en tiempo de importación en lugar de silenciosamente usar una cadena vacía.
# Esto garantiza que la aplicación nunca arranca en producción sin secreto,
# evitando que cualquier token firmado con "" sea válido para siempre.
_JWT_SECRET_RAW = os.getenv("FASTQR_JWT_SECRET", "")
if not _JWT_SECRET_RAW:
    raise RuntimeError(
        "FASTQR_JWT_SECRET environment variable is not set. "
        "Set it in your .env file or environment before starting the server."
    )
JWT_SECRET = _JWT_SECRET_RAW
JWT_ALGORITHM = os.getenv("FASTQR_JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("FASTQR_JWT_EXPIRE_MINUTES", "480"))


def hash_password(password: str) -> str:
    """Genera un hash bcrypt de la contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara texto plano contra hash bcrypt de forma segura (safe compare)."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(payload: dict, expires_minutes: int | None = None) -> str:
    """
    Genera un JWT firmado con HS256.

    Por qué timezone.utc en datetime.now():
    python-jose valida el campo 'exp' comparando UTC. Usar datetime.utcnow()
    (deprecated) puede causar problemas de consistencia de zona horaria en
    entornos con TZ configurada. timezone.utc es explícito y correcto.
    """
    expire_delta = timedelta(minutes=expires_minutes or JWT_EXPIRE_MINUTES)
    expire_at = datetime.now(timezone.utc) + expire_delta
    token_payload = {**payload, "exp": expire_at}
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    Decodifica y valida un JWT. Devuelve None si es inválido o ha expirado.

    Por qué devolver None en lugar de relanzar JWTError:
    Los callers (get_current_auth) solo necesitan saber si el token es válido
    o no. Ocultar la excepción evita filtrar detalles internos de la librería
    en mensajes de error al cliente.
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
