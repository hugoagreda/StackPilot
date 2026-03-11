from pydantic import BaseModel, Field


class ScoringSettingsUpdateRequest(BaseModel):
    vote_points: int = Field(..., ge=1, le=100)


class ScoringSettingsResponse(BaseModel):
    vote_points: int


class DishScoreBonusRequest(BaseModel):
    bonus_points: int = Field(..., ge=0, le=1000)


class DishScoreRow(BaseModel):
    dish_id: str
    dish_name: str
    votes: int
    vote_points: int
    bonus_points: int
    score: int


class DishScoresTodayResponse(BaseModel):
    date: str
    ranking: list[DishScoreRow]
