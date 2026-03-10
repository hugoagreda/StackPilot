from fastapi import APIRouter

from app.schemas.schedule import ScheduleRequest, ScheduleResponse
from app.services.booking_service import normalize_bookings
from app.services.calendar_service import render_ics
from app.services.cleaning_scheduler import generate_schedule

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/schedules/generate", response_model=ScheduleResponse)
def create_schedule(payload: ScheduleRequest) -> ScheduleResponse:
    bookings = normalize_bookings(payload.bookings)
    tasks, unscheduled = generate_schedule(
        bookings=bookings,
        cleaners=payload.cleaners,
        cleaning_duration_minutes=payload.cleaning_duration_minutes,
        fallback_window_hours=payload.fallback_window_hours,
    )

    calendar_ics = render_ics(tasks) if payload.include_calendar else None
    return ScheduleResponse(tasks=tasks, unscheduled=unscheduled, calendar_ics=calendar_ics)
