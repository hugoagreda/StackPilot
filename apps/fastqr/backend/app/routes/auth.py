from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.auth import LoginRequest, MeResponse, TokenResponse
from app.services.auth_service import authenticate_user, build_user_token
from app.utils.auth import CurrentAuth, get_current_auth

router = APIRouter(prefix="/auth")


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    # authenticate_user normaliza email a lowercase antes de la consulta;
    # devuelve None si el usuario no existe o si el hash no coincide —
    # ambos casos producen el mismo 401 para no filtrar si el email existe.
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = build_user_token(user)
    return TokenResponse(access_token=token)


@router.get("/me")
def me(
    # Buena práctica: anotar el tipo explícitamente (CurrentAuth en lugar de
    # Any) permite que mypy/pyright validen que accedemos solo a atributos
    # reales del dataclass, y hace la firma autodocumentable para quien lea
    # el código sin ejecutarlo.
    current_auth: CurrentAuth = Depends(get_current_auth),
) -> MeResponse:
    return MeResponse(
        user_id=current_auth.user_id,
        email=current_auth.email,
        role=current_auth.role,
        restaurant_id=current_auth.restaurant_id,
    )
