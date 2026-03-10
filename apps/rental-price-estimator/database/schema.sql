-- Core schema (MVP)
CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    state_region VARCHAR(120),
    country VARCHAR(120) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS neighborhoods (
    id SERIAL PRIMARY KEY,
    city_id INT NOT NULL REFERENCES cities(id),
    name VARCHAR(120) NOT NULL,
    demand_index NUMERIC(5,2),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(city_id, name)
);

CREATE TABLE IF NOT EXISTS properties (
    id UUID PRIMARY KEY,
    city_id INT NOT NULL REFERENCES cities(id),
    neighborhood_id INT NOT NULL REFERENCES neighborhoods(id),
    square_meters NUMERIC(10,2) NOT NULL,
    bedrooms INT NOT NULL,
    bathrooms INT NOT NULL,
    condition VARCHAR(30) NOT NULL,
    furnished BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS estimates (
    id UUID PRIMARY KEY,
    property_id UUID NOT NULL REFERENCES properties(id),
    estimated_rent NUMERIC(12,2) NOT NULL,
    lower_range NUMERIC(12,2) NOT NULL,
    upper_range NUMERIC(12,2) NOT NULL,
    price_per_sqm NUMERIC(10,2) NOT NULL,
    demand_level VARCHAR(20) NOT NULL,
    confidence_score NUMERIC(4,3),
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
