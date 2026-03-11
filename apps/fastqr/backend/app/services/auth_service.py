"""
app/services/auth_service.py — Lógica de autenticación de usuarios.

Responsabilidades:
- Verificar credenciales contra la BD (authenticate_user).
- Construir el payload JWT para un usuario (build_user_token).
- Buscar un usuario por ID al validar requests autenticados (get_user_by_id).
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.security import create_access_token, verify_password


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    # Normalizar email a lowercase antes de la consulta evita duplicados
    # silenciosos ("User@Example.com" vs "user@example.com") y es consistente
    # con cómo se almacenan los emails al registrar el usuario.
    stmt = select(User).where(User.email == email.lower().strip())
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        return None
    # Devolver None para "usuario no encontrado" y para "contraseña incorrecta"
    # es intencionado: evita enumerar si un email está registrado (timing-safe
    # en cuanto al mensaje, aunque no en cuanto a tiempo de respuesta).
    if not verify_password(password, user.password_hash):
        return None
    return user


def build_user_token(user: User) -> str:
    """
    Construye el JWT de acceso con los claims mínimos necesarios.

    Por qué incluir restaurant_id y role en el token:
    Los endpoints de dashboard necesitan estos valores en cada request.
    Incluirlos en el token evita una consulta extra a la BD en cada llamada
    autenticada — tradeoff aceptable porque ambos valores cambian raramente.
    """
    payload = {
        "sub": str(user.id),
        "restaurant_id": str(user.restaurant_id),
        "role": user.role,
        "email": user.email,
    }
    return create_access_token(payload)


def get_user_by_id(db: Session, user_id: str) -> User | None:
    # Validar el formato UUID antes de consultar evita que SQLAlchemy
    # lance un error de tipo si user_id llega malformado desde el token.
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return None
    stmt = select(User).where(User.id == user_uuid)
    return db.execute(stmt).scalar_one_or_none()
