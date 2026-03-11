"""
app/services/public_service.py — Lógica de negocio para endpoints públicos.

Endpoints servidos: menú, votos, feedback y ranking. Todos son accesibles sin
autenticación, pero pueden estar desactivados por el restaurante (feature flags
en RestaurantSetting). La función _enforce_table_access_policy gestiona el
cooldown anti-spam de escaneo de QR.
"""
import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.dish_score_override import DishScoreOverride
from app.models.dish import Dish
from app.models.feedback import Feedback
from app.models.scoring_setting import ScoringSetting
from app.models.table import Table
from app.models.table_access_session import TableAccessSession
from app.models.vote import Vote
from app.services.restaurant_service import (
    get_restaurant_feature_settings as _get_restaurant_feature_settings,
    get_table_and_restaurant_by_qr,
)
from app.utils.common import normalize_session_token as _normalize_session_token


def _as_utc(dt: datetime) -> datetime:
    # SQLite devuelve datetimes sin tzinfo aunque el valor esté guardado en UTC.
    # Añadir tzinfo=UTC permite comparar con datetime.now(timezone.utc) de forma segura.
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _normalize_comment(comment: str | None) -> str | None:
    if comment is None:
        return None
    normalized = comment.strip()
    return normalized or None


def _enforce_table_access_policy(db: Session, table: Table, session_token: str | None) -> None:
    """
    Aplica el cooldown de escaneo de QR por mesa y sesión.

    Por qué IntegrityError en lugar de SELECT-for-update:
    Capturar IntegrityError en el INSERT es el patrón "optimistic concurrency":
    asumir que la inserción va a funcionar y gestionar la colisión solo cuando
    ocurre. Es más eficiente que hacer un SELECT adicional para verificar cada vez,
    especialmente con tráfico bajo/medio donde la colisión es rara.
    """
    if not table.is_enabled:
        raise ValueError("Table QR is currently disabled")

    cooldown_minutes = max(int(table.scan_cooldown_minutes or 0), 0)
    if cooldown_minutes == 0:
        return

    if session_token is None:
        raise ValueError("session_token is required for table access policy")

    normalized_session_token = _normalize_session_token(session_token)
    stmt = select(TableAccessSession).where(
        TableAccessSession.table_id == table.id,
        TableAccessSession.session_token == normalized_session_token,
    )
    access_session = db.execute(stmt).scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if access_session is None:
        db.add(
            TableAccessSession(
                table_id=table.id,
                session_token=normalized_session_token,
                last_access_at=now,
            )
        )
        try:
            db.commit()
        except IntegrityError:
            # Concurrent request already inserted this session — treat as first access.
            db.rollback()
        return

    cooldown_until = _as_utc(access_session.last_access_at) + timedelta(minutes=cooldown_minutes)
    if now < cooldown_until:
        remaining = int((cooldown_until - now).total_seconds() // 60) + 1
        raise ValueError(f"Table access cooldown active, retry in {remaining} minute(s)")

    access_session.last_access_at = now
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def get_menu_by_qr(db: Session, qr_token: str, session_token: str | None = None) -> dict | None:
    table_restaurant = get_table_and_restaurant_by_qr(db, qr_token)
    if table_restaurant is None:
        return None

    table, restaurant = table_restaurant
    settings = _get_restaurant_feature_settings(db, restaurant.id)
    if not settings["allow_menu"]:
        return {"error": "feature_disabled", "feature": "menu"}

    _enforce_table_access_policy(db, table, session_token)

    categories_stmt = (
        select(Category)
        .where(Category.restaurant_id == restaurant.id)
        .order_by(Category.sort_order.asc(), Category.name.asc())
    )
    categories = db.execute(categories_stmt).scalars().all()

    dishes_stmt = (
        select(Dish)
        .where(Dish.restaurant_id == restaurant.id, Dish.is_available.is_(True))
        .order_by(Dish.name.asc())
    )
    dishes = db.execute(dishes_stmt).scalars().all()

    dishes_by_category: dict[uuid.UUID, list[Dish]] = defaultdict(list)
    for dish in dishes:
        dishes_by_category[dish.category_id].append(dish)

    response_categories: list[dict] = []
    for category in categories:
        response_categories.append(
            {
                "id": str(category.id),
                "name": category.name,
                "dishes": [
                    {
                        "id": str(dish.id),
                        "name": dish.name,
                        "description": dish.description,
                        "price_cents": dish.price_cents,
                    }
                    for dish in dishes_by_category.get(category.id, [])
                ],
            }
        )

    return {
        "restaurant": restaurant.name,
        "table": table.code,
        "categories": response_categories,
    }


def create_vote(db: Session, qr_token: str, dish_id: str, session_token: str) -> dict | None:
    table_restaurant = get_table_and_restaurant_by_qr(db, qr_token)
    if table_restaurant is None:
        return None

    table, restaurant = table_restaurant
    settings = _get_restaurant_feature_settings(db, restaurant.id)
    if not settings["allow_votes"]:
        return {"error": "feature_disabled", "feature": "votes"}

    normalized_session_token = _normalize_session_token(session_token)

    try:
        dish_uuid = uuid.UUID(dish_id)
    except ValueError:
        raise ValueError("Invalid dish_id format")

    dish_stmt = (
        select(Dish)
        .where(Dish.id == dish_uuid, Dish.restaurant_id == restaurant.id, Dish.is_available.is_(True))
    )
    dish = db.execute(dish_stmt).scalar_one_or_none()
    if dish is None:
        return {"error": "dish_not_found"}

    existing_stmt = select(Vote).where(
        Vote.restaurant_id == restaurant.id,
        Vote.dish_id == dish.id,
        Vote.session_token == normalized_session_token,
    )
    existing_vote = db.execute(existing_stmt).scalar_one_or_none()
    if existing_vote is not None:
        return {"status": "ignored", "reason": "already_voted", "dish_id": dish_id}

    vote = Vote(
        restaurant_id=restaurant.id,
        table_id=table.id,
        dish_id=dish.id,
        session_token=normalized_session_token,
        vote_date=date.today(),
    )
    db.add(vote)
    try:
        db.commit()
    except IntegrityError:
        # Race condition: dos requests simultáneos del mismo session_token/dish.
        # El segundo INSERT viola la restricción UNIQUE y se descarta de forma segura.
        db.rollback()
        return {"status": "ignored", "reason": "already_voted", "dish_id": dish_id}

    return {"status": "recorded", "dish_id": dish_id, "vote_date": str(vote.vote_date)}


def create_feedback(
    db: Session,
    qr_token: str,
    rating: int,
    comment: str | None,
    session_token: str,
) -> dict | None:
    table_restaurant = get_table_and_restaurant_by_qr(db, qr_token)
    if table_restaurant is None:
        return None

    table, restaurant = table_restaurant
    settings = _get_restaurant_feature_settings(db, restaurant.id)
    if not settings["allow_feedback"]:
        return {"error": "feature_disabled", "feature": "feedback"}

    normalized_session_token = _normalize_session_token(session_token)
    normalized_comment = _normalize_comment(comment)

    feedback = Feedback(
        restaurant_id=restaurant.id,
        table_id=table.id,
        rating=rating,
        comment=normalized_comment,
        session_id=normalized_session_token,
    )
    db.add(feedback)
    db.commit()

    return {"status": "received", "rating": rating}


def get_today_ranking(db: Session, qr_token: str) -> dict | None:
    table_restaurant = get_table_and_restaurant_by_qr(db, qr_token)
    if table_restaurant is None:
        return None

    _, restaurant = table_restaurant
    return _build_today_ranking_for_restaurant(db, restaurant.id)


def get_today_ranking_by_restaurant_id(db: Session, restaurant_id: str) -> dict:
    try:
        restaurant_uuid = uuid.UUID(restaurant_id)
    except ValueError as exc:
        raise ValueError("Invalid restaurant_id format") from exc

    return _build_today_ranking_for_restaurant(db, restaurant_uuid)


def _build_today_ranking_for_restaurant(db: Session, restaurant_id: uuid.UUID) -> dict:
    """
    Construye el ranking del día con soporte de puntuación ponderada.

    Diseño del JOIN:
    - INNER JOIN con Vote asegura que solo aparecen platos con al menos un voto.
    - LEFT OUTER JOIN con DishScoreOverride añade bonus_points opcionales por plato.
    Usar outerjoin evita excluir platos sin override; coalesce garantiza 0 si no hay.

    Motivo del .[:10]:
    El ranking muestra el Top 10. Truncar aquí (Python) en lugar de con .limit(10)
    en SQL es aceptable: DishScoreOverride.bonus_points es necesario para ordenar
    correctamente y no existe columna calculada en SQL para "score". Calcular en
    Python con los datos ya agrupados mantiene la query más simple.
    El antiguo .limit(50) erróneo ha sido eliminado — ahora se retorna el Top 10.
    """
    today = date.today()
    setting_stmt = select(ScoringSetting).where(ScoringSetting.restaurant_id == restaurant_id)
    scoring_setting = db.execute(setting_stmt).scalar_one_or_none()
    vote_points = scoring_setting.vote_points if scoring_setting is not None else 1

    ranking_stmt = (
        select(
            Dish.id,
            Dish.name,
            func.count(Vote.id).label("votes"),
            func.coalesce(func.max(DishScoreOverride.bonus_points), 0).label("bonus_points"),
        )
        .join(Vote, Vote.dish_id == Dish.id)
        .outerjoin(
            DishScoreOverride,
            (
                (DishScoreOverride.dish_id == Dish.id)
                & (DishScoreOverride.restaurant_id == restaurant_id)
                & (DishScoreOverride.score_date == today)
            ),
        )
        .where(Vote.restaurant_id == restaurant_id, Vote.vote_date == today)
        .group_by(Dish.id, Dish.name)
    )

    ranking_rows = db.execute(ranking_stmt).all()

    ranking_rows_with_score = [
        {
            "dish_id": str(row.id),
            "dish_name": row.name,
            "votes": int(row.votes),
            "vote_points": int(vote_points),
            "bonus_points": int(row.bonus_points),
            "score": int(row.votes) * int(vote_points) + int(row.bonus_points),
        }
        for row in ranking_rows
    ]

    ranking_rows_with_score.sort(key=lambda item: (-item["score"], item["dish_name"]))

    return {
        "date": str(today),
        "ranking": ranking_rows_with_score[:10],
    }
