import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class GameSession(Base):
    __tablename__ = "game_sessions"
    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "session_token",
            "game_type",
            "played_date",
            name="uq_game_session_daily",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    table_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tables.id"), nullable=False)
    session_token: Mapped[str] = mapped_column(String(120), nullable=False)
    game_type: Mapped[str] = mapped_column(String(30), nullable=False, default="spin_wheel")
    played_date: Mapped[date] = mapped_column(Date, nullable=False)
    reward_code: Mapped[str | None] = mapped_column(String(60), nullable=True, unique=True)
    reward_label: Mapped[str] = mapped_column(String(120), nullable=False)
    reward_status: Mapped[str] = mapped_column(String(20), nullable=False, default="issued")
    redeemed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
