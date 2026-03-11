import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.security import create_access_token, verify_password


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    stmt = select(User).where(User.email == email.lower().strip())
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def build_user_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "restaurant_id": str(user.restaurant_id),
        "role": user.role,
        "email": user.email,
    }
    return create_access_token(payload)


def get_user_by_id(db: Session, user_id: str) -> User | None:
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return None
    stmt = select(User).where(User.id == user_uuid)
    return db.execute(stmt).scalar_one_or_none()
