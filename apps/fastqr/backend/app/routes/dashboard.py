from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.analytics import OverviewResponse
from app.services.dashboard_service import get_overview

router = APIRouter(prefix="/dashboard")


@router.get("/overview")
def get_dashboard_overview(
    restaurant_slug: str | None = None,
    db: Session = Depends(get_db),
) -> OverviewResponse:
    overview = get_overview(db, restaurant_slug)
    return OverviewResponse(**overview)
