from pydantic import BaseModel, Field


class VoteRequest(BaseModel):
    dish_id: str = Field(..., description="UUID del plato")


class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=800)


class MenuDish(BaseModel):
    id: str
    name: str
    description: str | None = None
    price_cents: int


class MenuCategory(BaseModel):
    id: str
    name: str
    dishes: list[MenuDish]


class PublicMenuResponse(BaseModel):
    restaurant: str
    table: str
    categories: list[MenuCategory]
