from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.game import RewardResponse, SpinRequest, SpinResponse
from app.schemas.public import FeedbackRequest, PublicMenuResponse, VoteRequest
from app.services.game_service import get_session_reward, spin_wheel
from app.services.public_service import create_feedback, create_vote, get_menu_by_qr, get_today_ranking

router = APIRouter(prefix="/public")


# ---------------------------------------------------------------------------
# Helper privado de conversión de errores de servicio → HTTP
# ---------------------------------------------------------------------------
# Por qué existe _raise_for_feature_disabled:
# El patrón {"error": "feature_disabled", "feature": "..."} aparecía en 4
# endpoints distintos con el mismo bloque if/raise. Extraerlo a una función
# elimina la duplicación (DRY) y centraliza el código de estado HTTP:
# si el día de mañana queremos devolver 451 en lugar de 403, lo cambiamos
# en un solo sitio.
def _raise_for_feature_disabled(result: dict) -> None:
    """Lanza HTTP 403 si el servicio indica que la feature está desactivada."""
    if result.get("error") == "feature_disabled":
        raise HTTPException(status_code=403, detail=f"Feature disabled: {result['feature']}")


@router.get("/{qr_token}/menu")
def get_public_menu(
    qr_token: str,
    # session_token es opcional: el servicio ya declara el parámetro con
    # default None, por lo que pasarlo directamente es más limpio que
    # bifurcar "if session_token is None: call_a() else: call_b()".
    session_token: str | None = None,
    db: Session = Depends(get_db),
) -> PublicMenuResponse:
    try:
        menu = get_menu_by_qr(db, qr_token, session_token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if menu is None:
        raise HTTPException(status_code=404, detail="QR token not found")
    _raise_for_feature_disabled(menu)
    return PublicMenuResponse(**menu)


@router.post("/{qr_token}/votes")
def vote_dish(qr_token: str, payload: VoteRequest, db: Session = Depends(get_db)) -> dict:
    try:
        result = create_vote(db, qr_token, payload.dish_id, payload.session_token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="QR token not found")
    _raise_for_feature_disabled(result)
    if result.get("error") == "dish_not_found":
        raise HTTPException(status_code=404, detail="Dish not found for this restaurant")
    return result


@router.post("/{qr_token}/feedback")
def submit_feedback(qr_token: str, payload: FeedbackRequest, db: Session = Depends(get_db)) -> dict:
    try:
        result = create_feedback(db, qr_token, payload.rating, payload.comment, payload.session_token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="QR token not found")
    _raise_for_feature_disabled(result)
    return result


@router.get("/{qr_token}/ranking/today")
def get_ranking_today(qr_token: str, db: Session = Depends(get_db)) -> dict:
    ranking = get_today_ranking(db, qr_token)
    if ranking is None:
        raise HTTPException(status_code=404, detail="QR token not found")
    return ranking


@router.post("/{qr_token}/games/spin")
def spin_game(qr_token: str, payload: SpinRequest, db: Session = Depends(get_db)) -> SpinResponse:
    try:
        result = spin_wheel(db, qr_token, payload.session_token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="QR token not found")
    _raise_for_feature_disabled(result)
    return SpinResponse(**result)


@router.get("/{qr_token}/games/reward")
def get_game_reward(qr_token: str, session_token: str, db: Session = Depends(get_db)) -> RewardResponse:
    try:
        reward = get_session_reward(db, qr_token, session_token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if reward is None:
        raise HTTPException(status_code=404, detail="QR token not found")
    _raise_for_feature_disabled(reward)
    if reward.get("error") == "reward_not_found":
        raise HTTPException(status_code=404, detail="Reward not found for this session")
    return RewardResponse(**reward)
