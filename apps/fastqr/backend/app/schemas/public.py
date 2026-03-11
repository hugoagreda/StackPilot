from pydantic import AliasChoices, BaseModel, Field


class VoteRequest(BaseModel):
    dish_id: str = Field(..., description="UUID del plato")
    session_token: str = Field(
        ...,
        min_length=1,
        max_length=120,
        validation_alias=AliasChoices("session_token", "session_id"),
    )


class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=800)
    session_token: str = Field(
        ...,
        min_length=1,
        max_length=120,
        validation_alias=AliasChoices("session_token", "session_id"),
    )


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
