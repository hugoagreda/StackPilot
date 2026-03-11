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
    # El esquema actual de restaurant_settings no incluye columnas allow_*. Mantener
    # estas features activas evita errores de atributo y preserva comportamiento.
    return {
        "allow_menu": True,
        "allow_votes": True,
        "allow_feedback": True,
        "allow_games": True,
    }
