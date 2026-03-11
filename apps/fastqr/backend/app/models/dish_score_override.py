import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DishScoreOverride(Base):
    __tablename__ = "dish_score_overrides"
    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "dish_id",
            "score_date",
            name="uq_dish_score_override_daily",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    dish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("dishes.id"), nullable=False)
    score_date: Mapped[date] = mapped_column(Date, nullable=False)
    bonus_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
