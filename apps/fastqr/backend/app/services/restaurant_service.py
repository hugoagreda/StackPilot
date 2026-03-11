"""
Shared restaurant-level lookups used by multiple services.

Keeping these here avoids cross-service imports of private (_) functions
and breaks the circular dependency between public_service and game_service.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.models.restaurant_setting import RestaurantSetting
from app.models.table import Table


def get_table_and_restaurant_by_qr(db: Session, qr_token: str) -> tuple[Table, Restaurant] | None:
    stmt = (
        select(Table, Restaurant)
        .join(Restaurant, Restaurant.id == Table.restaurant_id)
        .where(Table.qr_token == qr_token)
    )
    result = db.execute(stmt).first()
    if result is None:
        return None
    return result[0], result[1]


def get_restaurant_feature_settings(db: Session, restaurant_id: uuid.UUID) -> dict:
    stmt = select(RestaurantSetting).where(RestaurantSetting.restaurant_id == restaurant_id)
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
