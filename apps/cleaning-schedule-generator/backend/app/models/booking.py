from sqlalchemy import Column, DateTime, ForeignKey, String

from app.models.property import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True)
    property_id = Column(String, ForeignKey("properties.id"), nullable=False, index=True)
    source = Column(String, nullable=False)
    external_id = Column(String, nullable=True)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
