from fastapi import APIRouter

router = APIRouter(prefix="/dashboard")


@router.get("/overview")
def get_overview() -> dict:
    return {
        "total_votes": 0,
        "unique_sessions": 0,
        "avg_rating": 0,
        "total_feedback": 0,
    }
