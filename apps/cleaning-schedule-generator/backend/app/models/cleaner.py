from sqlalchemy import Boolean, Column, DateTime, String

from app.models.property import Base


class Cleaner(Base):
    __tablename__ = "cleaners"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
