from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Property(Base):
    __tablename__ = "properties"

    id = Column(String, primary_key=True)
    host_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    timezone = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
