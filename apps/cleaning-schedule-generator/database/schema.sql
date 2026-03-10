CREATE TABLE properties (
    id VARCHAR(64) PRIMARY KEY,
    host_id VARCHAR(64) NOT NULL,
    name VARCHAR(120) NOT NULL,
    timezone VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE cleaners (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    phone VARCHAR(40),
    email VARCHAR(120),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE cleaner_availability (
    id BIGSERIAL PRIMARY KEY,
    cleaner_id VARCHAR(64) NOT NULL REFERENCES cleaners(id),
    day_of_week SMALLINT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE bookings (
    id VARCHAR(64) PRIMARY KEY,
    property_id VARCHAR(64) NOT NULL REFERENCES properties(id),
    source VARCHAR(40) NOT NULL,
    external_id VARCHAR(100),
    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE cleaning_tasks (
    id VARCHAR(64) PRIMARY KEY,
    booking_id VARCHAR(64) NOT NULL REFERENCES bookings(id),
    property_id VARCHAR(64) NOT NULL REFERENCES properties(id),
    cleaner_id VARCHAR(64) NOT NULL REFERENCES cleaners(id),
    start_at TIMESTAMP NOT NULL,
    end_at TIMESTAMP NOT NULL,
    status VARCHAR(30) NOT NULL,
    exported_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bookings_property_dates ON bookings(property_id, check_in, check_out);
CREATE INDEX idx_tasks_cleaner_time ON cleaning_tasks(cleaner_id, start_at, end_at);
