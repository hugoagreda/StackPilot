from sqlalchemy import Column, DateTime, ForeignKey, String

from app.models.property import Base


class CleaningTask(Base):
    __tablename__ = "cleaning_tasks"

    id = Column(String, primary_key=True)
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False, index=True)
    property_id = Column(String, ForeignKey("properties.id"), nullable=False, index=True)
    cleaner_id = Column(String, ForeignKey("cleaners.id"), nullable=False, index=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
