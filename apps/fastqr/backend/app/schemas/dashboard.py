from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)


class CategoryResponse(BaseModel):
    id: str
    name: str


class TableCreateRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)


class TableResponse(BaseModel):
    id: str
    restaurant_id: str
    code: str
    qr_token: str
    is_enabled: bool
    scan_cooldown_minutes: int


class TablePolicyUpdateRequest(BaseModel):
    is_enabled: bool | None = None
    scan_cooldown_minutes: int | None = Field(default=None, ge=0, le=1440)


class TablePolicyResponse(BaseModel):
    table_id: str
    is_enabled: bool
    scan_cooldown_minutes: int


class DishCreateRequest(BaseModel):
    category_id: str
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1200)
    price_cents: int = Field(..., ge=0)
    image_url: str | None = Field(default=None, max_length=255)
    is_available: bool = True


class DishUpdateRequest(BaseModel):
    category_id: str | None = None
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1200)
    price_cents: int | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=255)
    is_available: bool | None = None


class DishResponse(BaseModel):
    id: str
    restaurant_id: str
    category_id: str
    name: str
    description: str | None = None
    price_cents: int
    image_url: str | None = None
    is_available: bool


class RestaurantFeatureSettingsResponse(BaseModel):
    allow_menu: bool
    allow_votes: bool
    allow_feedback: bool
    allow_games: bool


class RestaurantFeatureSettingsUpdateRequest(BaseModel):
    allow_menu: bool | None = None
    allow_votes: bool | None = None
    allow_feedback: bool | None = None
    allow_games: bool | None = None
