"""
app/services/dashboard_service.py — CRUD del dashboard para el restaurante autenticado.

Responsabilidades: categorías, platos, tablas, configuración de features,
ajustes de scoring y métricas de overview. Todos los métodos reciben el
restaurant_id como string y lo validan con _parse_uuid antes de usarlo en
queries, centralizando la conversión UUID en un único punto.
"""
import uuid
from datetime import date

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.dish_score_override import DishScoreOverride
from app.models.dish import Dish
from app.models.feedback import Feedback
from app.models.restaurant import Restaurant
from app.models.restaurant_setting import RestaurantSetting
from app.models.scoring_setting import ScoringSetting
from app.models.table import Table
from app.models.vote import Vote
from app.utils.common import parse_uuid as _parse_uuid


def _compute_overview_metrics(db: Session, restaurant_id: uuid.UUID) -> dict:
    """
    Ejecuta 4 COUNT/AVG en una sola función para evitar duplicar la lógica.

    Por qué una función privada en lugar de inlinarla dos veces:
    get_overview() y get_overview_by_restaurant_id() necesitaban el mismo bloque
    de 4 queries. Extraerlo garantiza que cualquier cambio en las métricas
    (p.ej. añadir total_tables) solo se hace en un lugar — principio DRY.
    """
    votes_stmt = select(func.count(Vote.id)).where(Vote.restaurant_id == restaurant_id)
    unique_sessions_stmt = select(func.count(distinct(Vote.session_token))).where(
        Vote.restaurant_id == restaurant_id
    )
    feedback_count_stmt = select(func.count(Feedback.id)).where(Feedback.restaurant_id == restaurant_id)
    avg_rating_stmt = select(func.avg(Feedback.rating)).where(Feedback.restaurant_id == restaurant_id)

    total_votes = db.execute(votes_stmt).scalar_one() or 0
    unique_sessions = db.execute(unique_sessions_stmt).scalar_one() or 0
    total_feedback = db.execute(feedback_count_stmt).scalar_one() or 0
    avg_rating_raw = db.execute(avg_rating_stmt).scalar_one()

    return {
        "total_votes": int(total_votes),
        "unique_sessions": int(unique_sessions),
        "avg_rating": float(avg_rating_raw) if avg_rating_raw is not None else 0.0,
        "total_feedback": int(total_feedback),
    }


def get_overview(db: Session, restaurant_slug: str | None = None) -> dict:
    if restaurant_slug:
        restaurant_stmt = select(Restaurant).where(Restaurant.slug == restaurant_slug)
    else:
        restaurant_stmt = select(Restaurant).order_by(Restaurant.created_at.asc())

    restaurant = db.execute(restaurant_stmt).scalars().first()
    if restaurant is None:
        return {
            "total_votes": 0,
            "unique_sessions": 0,
            "avg_rating": 0.0,
            "total_feedback": 0,
        }

    return _compute_overview_metrics(db, restaurant.id)


def list_categories(db: Session, restaurant_id: str) -> list[Category]:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    stmt = (
        select(Category)
        .where(Category.restaurant_id == restaurant_uuid)
        .order_by(Category.sort_order.asc(), Category.name.asc())
    )
    return db.execute(stmt).scalars().all()


def create_category(db: Session, restaurant_id: str, name: str) -> Category:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    normalized = name.strip()
    if not normalized:
        raise ValueError("Category name cannot be empty")
    category = Category(
        restaurant_id=restaurant_uuid,
        name=normalized,
        sort_order=0,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_overview_by_restaurant_id(db: Session, restaurant_id: str) -> dict:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    return _compute_overview_metrics(db, restaurant_uuid)


def list_tables(db: Session, restaurant_id: str) -> list[Table]:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    stmt = select(Table).where(Table.restaurant_id == restaurant_uuid).order_by(Table.code.asc())
    return db.execute(stmt).scalars().all()


def create_table(db: Session, restaurant_id: str, code: str) -> Table:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    normalized_code = code.strip()
    if not normalized_code:
        raise ValueError("Table code cannot be empty")

    table = Table(
        restaurant_id=restaurant_uuid,
        code=normalized_code,
        qr_token=str(uuid.uuid4()),
        is_enabled=True,
        scan_cooldown_minutes=10,
    )
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def list_dishes(db: Session, restaurant_id: str) -> list[Dish]:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    stmt = (
        select(Dish)
        .where(Dish.restaurant_id == restaurant_uuid)
        .order_by(Dish.is_available.desc(), Dish.name.asc())
    )
    return db.execute(stmt).scalars().all()


def create_dish(
    db: Session,
    restaurant_id: str,
    category_id: str,
    name: str,
    description: str | None,
    price_cents: int,
    image_url: str | None,
    is_available: bool,
) -> Dish:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    category_uuid = _parse_uuid(category_id, "category_id")

    category_stmt = select(Category).where(
        Category.id == category_uuid,
        Category.restaurant_id == restaurant_uuid,
    )
    category = db.execute(category_stmt).scalar_one_or_none()
    if category is None:
        raise ValueError("Category not found for this restaurant")

    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("Dish name cannot be empty")

    dish = Dish(
        restaurant_id=restaurant_uuid,
        category_id=category_uuid,
        name=normalized_name,
        description=description.strip() if description else None,
        price_cents=price_cents,
        image_url=image_url.strip() if image_url else None,
        is_available=is_available,
    )
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish


def update_dish(
    db: Session,
    restaurant_id: str,
    dish_id: str,
    category_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    price_cents: int | None = None,
    image_url: str | None = None,
    is_available: bool | None = None,
) -> Dish | None:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    dish_uuid = _parse_uuid(dish_id, "dish_id")

    dish_stmt = select(Dish).where(Dish.id == dish_uuid, Dish.restaurant_id == restaurant_uuid)
    dish = db.execute(dish_stmt).scalar_one_or_none()
    if dish is None:
        return None

    if category_id is not None:
        category_uuid = _parse_uuid(category_id, "category_id")
        category_stmt = select(Category).where(
            Category.id == category_uuid,
            Category.restaurant_id == restaurant_uuid,
        )
        category = db.execute(category_stmt).scalar_one_or_none()
        if category is None:
            raise ValueError("Category not found for this restaurant")
        dish.category_id = category_uuid

    if name is not None:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Dish name cannot be empty")
        dish.name = normalized_name
    if description is not None:
        dish.description = description.strip() or None
    if price_cents is not None:
        dish.price_cents = price_cents
    if image_url is not None:
        dish.image_url = image_url.strip() or None
    if is_available is not None:
        dish.is_available = is_available

    db.commit()
    db.refresh(dish)
    return dish


def get_scoring_settings(db: Session, restaurant_id: str) -> dict:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    stmt = select(ScoringSetting).where(ScoringSetting.restaurant_id == restaurant_uuid)
    setting = db.execute(stmt).scalar_one_or_none()
    if setting is None:
        return {"vote_points": 1}
    return {"vote_points": setting.vote_points}


def update_scoring_settings(db: Session, restaurant_id: str, vote_points: int) -> dict:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    stmt = select(ScoringSetting).where(ScoringSetting.restaurant_id == restaurant_uuid)
    setting = db.execute(stmt).scalar_one_or_none()

    if setting is None:
        setting = ScoringSetting(restaurant_id=restaurant_uuid, vote_points=vote_points)
        db.add(setting)
    else:
        setting.vote_points = vote_points

    db.commit()
    return {"vote_points": vote_points}


def set_dish_score_bonus_today(db: Session, restaurant_id: str, dish_id: str, bonus_points: int) -> dict | None:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    dish_uuid = _parse_uuid(dish_id, "dish_id")
    today = date.today()

    dish_stmt = select(Dish).where(Dish.id == dish_uuid, Dish.restaurant_id == restaurant_uuid)
    dish = db.execute(dish_stmt).scalar_one_or_none()
    if dish is None:
        return None

    override_stmt = select(DishScoreOverride).where(
        DishScoreOverride.restaurant_id == restaurant_uuid,
        DishScoreOverride.dish_id == dish_uuid,
        DishScoreOverride.score_date == today,
    )
    override = db.execute(override_stmt).scalar_one_or_none()
    if override is None:
        override = DishScoreOverride(
            restaurant_id=restaurant_uuid,
            dish_id=dish_uuid,
            score_date=today,
            bonus_points=bonus_points,
        )
        db.add(override)
    else:
        override.bonus_points = bonus_points

    db.commit()
    return {
        "dish_id": dish_id,
        "bonus_points": bonus_points,
    }


def get_restaurant_feature_settings(db: Session, restaurant_id: str) -> dict:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    stmt = select(RestaurantSetting).where(RestaurantSetting.restaurant_id == restaurant_uuid)
    setting = db.execute(stmt).scalar_one_or_none()
    if setting is None:
        return {
            "allow_menu": True,
            "allow_votes": True,
            "allow_feedback": True,
            "allow_games": True,
        }
    return {
        "allow_menu": setting.allow_menu,
        "allow_votes": setting.allow_votes,
        "allow_feedback": setting.allow_feedback,
        "allow_games": setting.allow_games,
    }


def update_restaurant_feature_settings(
    db: Session,
    restaurant_id: str,
    allow_menu: bool | None = None,
    allow_votes: bool | None = None,
    allow_feedback: bool | None = None,
    allow_games: bool | None = None,
) -> dict:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    stmt = select(RestaurantSetting).where(RestaurantSetting.restaurant_id == restaurant_uuid)
    setting = db.execute(stmt).scalar_one_or_none()
    if setting is None:
        setting = RestaurantSetting(restaurant_id=restaurant_uuid)
        db.add(setting)

    if allow_menu is not None:
        setting.allow_menu = allow_menu
    if allow_votes is not None:
        setting.allow_votes = allow_votes
    if allow_feedback is not None:
        setting.allow_feedback = allow_feedback
    if allow_games is not None:
        setting.allow_games = allow_games

    db.commit()
    return {
        "allow_menu": setting.allow_menu,
        "allow_votes": setting.allow_votes,
        "allow_feedback": setting.allow_feedback,
        "allow_games": setting.allow_games,
    }


def update_table_policy(
    db: Session,
    restaurant_id: str,
    table_id: str,
    is_enabled: bool | None = None,
    scan_cooldown_minutes: int | None = None,
) -> dict | None:
    restaurant_uuid = _parse_uuid(restaurant_id, "restaurant_id")
    table_uuid = _parse_uuid(table_id, "table_id")

    stmt = select(Table).where(Table.id == table_uuid, Table.restaurant_id == restaurant_uuid)
    table = db.execute(stmt).scalar_one_or_none()
    if table is None:
        return None

    if is_enabled is not None:
        table.is_enabled = is_enabled
    if scan_cooldown_minutes is not None:
        table.scan_cooldown_minutes = scan_cooldown_minutes

    db.commit()
    return {
        "table_id": str(table.id),
        "is_enabled": table.is_enabled,
        "scan_cooldown_minutes": table.scan_cooldown_minutes,
    }
