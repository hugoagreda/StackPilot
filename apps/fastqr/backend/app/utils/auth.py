from dataclasses import dataclass
import logging
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.restaurant import Restaurant
from app.services.auth_service import get_user_by_id
from app.utils.security import decode_access_token

logger = logging.getLogger(__name__)

# tokenUrl apunta al endpoint de login para que la UI de Swagger /docs
# muestre un formulario de autenticación funcional.
# auto_error=False permite que el token sea None cuando no se envía — la
# función get_current_auth decide entonces si lanzar 401 o usar dev auth.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# ---------------------------------------------------------------------------
# Bypass de autenticación (solo desarrollo local)
# ---------------------------------------------------------------------------
# Buena práctica: evaluar la variable de entorno UNA SOLA VEZ en tiempo de
# importación, no en cada request. Así, si alguien inyecta la variable en
# tiempo de ejecución (no es posible, pero por defensa en profundidad) el
# valor ya quedó fijo. Además un proceso que arrancó con bypass se puede
# loggear de forma definitiva al arrancar.
_AUTH_DISABLED: bool = os.getenv("FASTQR_DISABLE_AUTH", "").strip().lower() in {"1", "true", "yes", "on"}
if _AUTH_DISABLED:
    logger.warning(
        "FASTQR_DISABLE_AUTH is active — all dashboard authentication is BYPASSED. "
        "Never enable this in production."
    )


@dataclass
class CurrentAuth:
    """Información del usuario autenticado inyectada vía Depends()."""
    user_id: str
    email: str
    role: str
    restaurant_id: str


def _is_auth_disabled() -> bool:
    return _AUTH_DISABLED


def _build_dev_auth(db: Session) -> CurrentAuth:
    """
    Construye un CurrentAuth ficticio apuntando al primer restaurante de la BD.
    Solo se llama cuando _AUTH_DISABLED = True.
    """
    restaurant = db.execute(select(Restaurant).order_by(Restaurant.created_at.asc())).scalars().first()
    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No restaurant found for dev auth",
        )
    return CurrentAuth(
        user_id="dev-user",
        email="dev@fastqr.local",
        role="manager",
        restaurant_id=str(restaurant.id),
    )


def get_current_auth(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> CurrentAuth:
    """
    Dependencia FastAPI que valida el JWT y devuelve el CurrentAuth del request.

    Flujo:
    1. Si el bypass está activo → devuelve un CurrentAuth de desarrollo.
    2. Si no hay token → 401.
    3. Si el token es inválido o expirado → 401.
    4. Verifica en BD que el usuario todavía existe.
    5. Devuelve CurrentAuth con los datos del token + los del usuario real.

    Por qué comprobar el usuario en BD (paso 4):
    Un JWT válido no significa que el usuario aún exista. Si el usuario
    fue eliminado, el token seguiría siendo criptográficamente válido.
    """
    if _is_auth_disabled():
        return _build_dev_auth(db)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    restaurant_id = payload.get("restaurant_id")
    role = payload.get("role")
    email = payload.get("email")

    if not user_id or not restaurant_id or not role or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return CurrentAuth(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        restaurant_id=str(user.restaurant_id),
    )
