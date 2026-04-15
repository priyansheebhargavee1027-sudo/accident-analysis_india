-- ================================================================
-- sql/queries.sql
-- India Traffic Accident Analysis — Analytical Queries
-- ================================================================


-- ── 1. TOP 10 STATES BY TOTAL ACCIDENTS ─────────────────────────
SELECT
    state,
    COUNT(*)                                      AS total_accidents,
    SUM(fatalities)                               AS total_fatalities,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct
FROM accidents
GROUP BY state
ORDER BY total_accidents DESC
LIMIT 10;


-- ── 2. TOP 15 ACCIDENT-PRONE DISTRICTS ──────────────────────────
SELECT
    state,
    district,
    COUNT(*)        AS total_accidents,
    SUM(fatalities) AS total_fatalities
FROM accidents
GROUP BY state, district
ORDER BY total_accidents DESC
LIMIT 15;


-- ── 3. HOURLY ACCIDENT DISTRIBUTION ─────────────────────────────
SELECT
    hour,
    COUNT(*)                                      AS accidents,
    SUM(fatalities)                               AS fatalities,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct
FROM accidents
GROUP BY hour
ORDER BY hour;


-- ── 4. DAY vs NIGHT COMPARISON ───────────────────────────────────
SELECT
    is_night,
    COUNT(*)                                      AS accidents,
    SUM(fatalities)                               AS fatalities,
    SUM(injuries)                                 AS injuries,
    ROUND(AVG(total_casualties), 2)               AS avg_casualties_per_accident,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct
FROM accidents
GROUP BY is_night;


-- ── 5. ACCIDENT CAUSE BREAKDOWN ──────────────────────────────────
SELECT
    cause,
    COUNT(*)                                      AS accidents,
    SUM(fatalities)                               AS fatalities,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct,
    ROUND(AVG(injuries), 2)                       AS avg_injuries
FROM accidents
GROUP BY cause
ORDER BY fatalities DESC;


-- ── 6. ROAD TYPE RISK ANALYSIS ───────────────────────────────────
SELECT
    road_type,
    COUNT(*)                                      AS accidents,
    SUM(fatalities)                               AS fatalities,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct,
    ROUND(AVG(num_vehicles), 2)                   AS avg_vehicles_involved
FROM accidents
GROUP BY road_type
ORDER BY fatality_rate_pct DESC;


-- ── 7. YEARLY TREND ──────────────────────────────────────────────
SELECT
    year,
    COUNT(*)        AS accidents,
    SUM(fatalities) AS fatalities,
    SUM(injuries)   AS injuries,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct
FROM accidents
GROUP BY year
ORDER BY year;


-- ── 8. MONTHLY SEASONALITY ───────────────────────────────────────
SELECT
    month,
    month_name,
    COUNT(*)                        AS accidents,
    SUM(fatalities)                 AS fatalities,
    ROUND(AVG(total_casualties), 2) AS avg_casualties
FROM accidents
GROUP BY month, month_name
ORDER BY month;


-- ── 9. WEEKDAY PATTERN ───────────────────────────────────────────
SELECT
    weekday,
    COUNT(*)        AS accidents,
    SUM(fatalities) AS fatalities,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct
FROM accidents
GROUP BY weekday
ORDER BY
    CASE weekday
        WHEN 'Monday'    THEN 1
        WHEN 'Tuesday'   THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday'  THEN 4
        WHEN 'Friday'    THEN 5
        WHEN 'Saturday'  THEN 6
        WHEN 'Sunday'    THEN 7
    END;


-- ── 10. SEVERITY DISTRIBUTION ────────────────────────────────────
SELECT
    severity,
    COUNT(*)                                 AS accidents,
    ROUND(COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM accidents), 2) AS pct_of_total
FROM accidents
GROUP BY severity
ORDER BY accidents DESC;


-- ── 11. WEATHER IMPACT ───────────────────────────────────────────
SELECT
    weather,
    COUNT(*)                                      AS accidents,
    SUM(fatalities)                               AS fatalities,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct
FROM accidents
GROUP BY weather
ORDER BY fatalities DESC;


-- ── 12. VEHICLE TYPE ANALYSIS ────────────────────────────────────
SELECT
    vehicle_type,
    COUNT(*)        AS accidents,
    SUM(fatalities) AS fatalities,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct
FROM accidents
GROUP BY vehicle_type
ORDER BY accidents DESC;


-- ── 13. HIGH-RISK TIME SLOTS (STATE + HOUR) ──────────────────────
SELECT
    state,
    hour,
    COUNT(*) AS accidents
FROM accidents
WHERE severity = 'Fatal'
GROUP BY state, hour
ORDER BY accidents DESC
LIMIT 20;


-- ── 14. BLACK SPOTS — TOP DISTRICT × ROAD TYPE COMBINATIONS ─────
SELECT
    state,
    district,
    road_type,
    COUNT(*)                                      AS accidents,
    SUM(fatalities)                               AS fatalities,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct
FROM accidents
GROUP BY state, district, road_type
HAVING accidents >= 50
ORDER BY fatalities DESC
LIMIT 20;


-- ── 15. WEEKEND vs WEEKDAY FATALITY RATE ────────────────────────
SELECT
    CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(*)                                      AS accidents,
    SUM(fatalities)                               AS fatalities,
    ROUND(SUM(fatalities) * 100.0 / COUNT(*), 2) AS fatality_rate_pct
FROM accidents
GROUP BY is_weekend;
