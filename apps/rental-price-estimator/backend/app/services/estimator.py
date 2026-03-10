from app.schemas.estimate import EstimateRequest, EstimateResponse


def estimate_rent(payload: EstimateRequest) -> EstimateResponse:
    # Baseline MVP heuristic; replace with comparables + ML in next iteration.
    base_price_per_sqm = 12.0
    bedroom_weight = 35.0
    bathroom_weight = 25.0
    condition_factor = {
        "poor": 0.85,
        "fair": 0.95,
        "good": 1.00,
        "renovated": 1.12,
        "premium": 1.25,
    }.get(payload.condition.lower(), 1.0)
    furnished_factor = 1.10 if payload.furnished else 1.0

    estimated_rent = (
        payload.square_meters * base_price_per_sqm
        + payload.bedrooms * bedroom_weight
        + payload.bathrooms * bathroom_weight
    ) * condition_factor * furnished_factor

    lower_range = estimated_rent * 0.9
    upper_range = estimated_rent * 1.1
    price_per_sqm = estimated_rent / payload.square_meters

    demand_level = "medium"
    if price_per_sqm < 10:
        demand_level = "high"
    elif price_per_sqm > 18:
        demand_level = "low"

    return EstimateResponse(
        estimated_rent=round(estimated_rent, 2),
        lower_range=round(lower_range, 2),
        upper_range=round(upper_range, 2),
        price_per_sqm=round(price_per_sqm, 2),
        demand_level=demand_level,
    )
