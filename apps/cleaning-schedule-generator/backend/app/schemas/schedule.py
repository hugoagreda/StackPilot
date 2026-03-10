from datetime import datetime

from pydantic import BaseModel, Field


class BookingInput(BaseModel):
    booking_id: str
    property_id: str
    check_in: datetime
    check_out: datetime


class AvailabilityWindow(BaseModel):
    start: datetime
    end: datetime


class CleanerInput(BaseModel):
    cleaner_id: str
    name: str
    availability: list[AvailabilityWindow]


class ScheduleRequest(BaseModel):
    bookings: list[BookingInput]
    cleaners: list[CleanerInput]
    cleaning_duration_minutes: int = Field(default=120, ge=30, le=600)
    fallback_window_hours: int = Field(default=24, ge=1, le=72)
    include_calendar: bool = True


class ScheduleTask(BaseModel):
    booking_id: str
    property_id: str
    cleaner_id: str
    cleaner_name: str
    start: datetime
    end: datetime


class UnscheduledTask(BaseModel):
    booking_id: str
    property_id: str
    reason: str


class ScheduleResponse(BaseModel):
    tasks: list[ScheduleTask]
    unscheduled: list[UnscheduledTask]
    calendar_ics: str | None = None
