import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class RestaurantSetting(Base):
    __tablename__ = "restaurant_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("restaurants.id"),
        nullable=False,
        unique=True,
    )
    allow_menu: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_votes: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_feedback: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_games: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
