from fastapi import APIRouter

from app.schemas.estimate import EstimateRequest, EstimateResponse
from app.services.estimator import estimate_rent

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/estimates", response_model=EstimateResponse)
def create_estimate(payload: EstimateRequest) -> EstimateResponse:
    return estimate_rent(payload)
