from dataclasses import dataclass
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.restaurant import Restaurant
from app.services.auth_service import get_user_by_id
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


@dataclass
class CurrentAuth:
    user_id: str
    email: str
    role: str
    restaurant_id: str


def _is_auth_disabled() -> bool:
    raw = os.getenv("FASTQR_DISABLE_AUTH", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _build_dev_auth(db: Session) -> CurrentAuth:
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
