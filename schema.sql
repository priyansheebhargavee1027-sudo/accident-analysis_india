-- ================================================================
-- sql/schema.sql
-- India Traffic Accident Analysis — Database Schema
-- Compatible with: SQLite 3 / PostgreSQL
-- ================================================================

-- Main accident table
CREATE TABLE IF NOT EXISTS accidents (
    accident_id     TEXT PRIMARY KEY,
    datetime        TIMESTAMP NOT NULL,
    year            INTEGER,
    month           INTEGER,
    month_name      TEXT,
    hour            INTEGER,
    weekday         TEXT,
    quarter         INTEGER,
    day_period      TEXT,
    is_night        TEXT,          -- 'Day' | 'Night'
    is_weekend      INTEGER,       -- 0 | 1
    state           TEXT NOT NULL,
    district        TEXT,
    latitude        REAL,
    longitude       REAL,
    road_type       TEXT,
    cause           TEXT,
    vehicle_type    TEXT,
    num_vehicles    INTEGER,
    collision_type  TEXT,
    weather         TEXT,
    road_surface    TEXT,
    severity        TEXT,          -- 'Minor' | 'Grievous' | 'Fatal'
    fatalities      INTEGER DEFAULT 0,
    injuries        INTEGER DEFAULT 0,
    total_casualties INTEGER,
    is_fatal        INTEGER        -- 0 | 1
);

-- State-level summary
CREATE TABLE IF NOT EXISTS state_summary (
    state               TEXT PRIMARY KEY,
    total_accidents     INTEGER,
    total_fatalities    INTEGER,
    total_injuries      INTEGER,
    fatal_accidents     INTEGER,
    fatality_rate_pct   REAL,
    risk_score          REAL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_state    ON accidents(state);
CREATE INDEX IF NOT EXISTS idx_year     ON accidents(year);
CREATE INDEX IF NOT EXISTS idx_hour     ON accidents(hour);
CREATE INDEX IF NOT EXISTS idx_severity ON accidents(severity);
CREATE INDEX IF NOT EXISTS idx_cause    ON accidents(cause);
CREATE INDEX IF NOT EXISTS idx_is_night ON accidents(is_night);
CREATE INDEX IF NOT EXISTS idx_road_type ON accidents(road_type);
