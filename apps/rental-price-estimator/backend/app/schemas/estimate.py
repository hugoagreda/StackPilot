from pydantic import BaseModel, Field


class EstimateRequest(BaseModel):
    city: str = Field(min_length=2)
    neighborhood: str = Field(min_length=2)
    square_meters: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    bathrooms: int = Field(ge=0)
    condition: str
    furnished: bool


class EstimateResponse(BaseModel):
    estimated_rent: float
    lower_range: float
    upper_range: float
    price_per_sqm: float
    demand_level: str
