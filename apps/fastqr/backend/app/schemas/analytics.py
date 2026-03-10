from pydantic import BaseModel


class OverviewResponse(BaseModel):
    total_votes: int
    unique_sessions: int
    avg_rating: float
    total_feedback: int
