from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.auth import LoginRequest, MeResponse, TokenResponse
from app.services.auth_service import authenticate_user, build_user_token
from app.utils.auth import get_current_auth

router = APIRouter(prefix="/auth")


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = build_user_token(user)
    return TokenResponse(access_token=token)


@router.get("/me")
def me(current_auth=Depends(get_current_auth)) -> MeResponse:
    return MeResponse(
        user_id=current_auth.user_id,
        email=current_auth.email,
        role=current_auth.role,
        restaurant_id=current_auth.restaurant_id,
    )
