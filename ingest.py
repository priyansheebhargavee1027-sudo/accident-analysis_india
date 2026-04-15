"""
scripts/ingest.py
-----------------
Downloads or generates India road accident data.
Produces: data/raw/accidents.csv
"""

import os
import random
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent
RAW_DIR    = ROOT / "data" / "raw"
PROC_DIR   = ROOT / "data" / "processed"
DB_PATH    = ROOT / "data" / "accidents.db"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)

# ── Constants ─────────────────────────────────────────────────────────────────
STATES = [
    "Uttar Pradesh", "Tamil Nadu", "Maharashtra", "Madhya Pradesh",
    "Karnataka", "Rajasthan", "Andhra Pradesh", "Gujarat",
    "West Bengal", "Telangana", "Bihar", "Kerala",
    "Haryana", "Punjab", "Delhi", "Odisha",
]

DISTRICTS = {
    "Uttar Pradesh":  ["Lucknow", "Kanpur", "Agra", "Varanasi", "Prayagraj"],
    "Tamil Nadu":     ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli"],
    "Maharashtra":    ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain"],
    "Karnataka":      ["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Belagavi"],
    "Rajasthan":      ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Kurnool"],
    "Gujarat":        ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
    "West Bengal":    ["Kolkata", "Howrah", "Asansol", "Siliguri", "Durgapur"],
    "Telangana":      ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
    "Bihar":          ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia"],
    "Kerala":         ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kannur"],
    "Haryana":        ["Gurugram", "Faridabad", "Panipat", "Ambala", "Hisar"],
    "Punjab":         ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
    "Delhi":          ["Central Delhi", "South Delhi", "North Delhi", "East Delhi", "West Delhi"],
    "Odisha":         ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"],
}

ROAD_TYPES      = ["National Highway", "State Highway", "District Road", "Urban Road", "Rural Road"]
CAUSES          = [
    "Over Speeding", "Drunk Driving", "Jumping Red Light",
    "Distracted Driving", "Wrong Side Driving", "Poor Road Condition",
    "Vehicle Defect", "Bad Weather", "Pedestrian Error", "Other",
]
VEHICLE_TYPES   = ["Car/Jeep", "Two Wheeler", "Truck/Lorry", "Bus", "Auto Rickshaw", "Bicycle", "Other"]
WEATHER_COND    = ["Clear", "Rainy", "Foggy", "Cloudy", "Hazy"]
ROAD_SURFACE    = ["Dry", "Wet", "Muddy", "Under Construction"]
COLLISION_TYPES = ["Head-on", "Rear-end", "Side-impact", "Rollover", "Hit & Run", "Pedestrian"]

# State-level risk weights (higher = more accidents relative to size)
STATE_WEIGHTS = {
    "Uttar Pradesh": 0.18, "Tamil Nadu": 0.12, "Maharashtra": 0.11,
    "Madhya Pradesh": 0.09, "Karnataka": 0.08, "Rajasthan": 0.07,
    "Andhra Pradesh": 0.06, "Gujarat": 0.06, "West Bengal": 0.05,
    "Telangana": 0.04, "Bihar": 0.04, "Kerala": 0.04,
    "Haryana": 0.03, "Punjab": 0.03, "Delhi": 0.03, "Odisha": 0.02,
}

# Hour-of-day risk profile (0–23)
HOUR_RISK = np.array([
    0.5, 0.4, 0.3, 0.3, 0.3, 0.5,   # 00-05
    0.8, 1.2, 1.5, 1.3, 1.1, 1.2,   # 06-11
    1.3, 1.2, 1.0, 1.0, 1.1, 1.4,   # 12-17
    1.6, 1.5, 1.3, 1.0, 0.8, 0.6,   # 18-23
])
HOUR_RISK /= HOUR_RISK.sum()


def generate_synthetic_data(n: int = 50_000) -> pd.DataFrame:
    """Generate realistic synthetic accident records."""
    logger.info(f"Generating {n:,} synthetic accident records…")

    rng = np.random.default_rng(42)

    # Dates: Jan 2018 – Dec 2023
    start = datetime(2018, 1, 1)
    end   = datetime(2023, 12, 31)
    days  = (end - start).days
    random_days  = rng.integers(0, days, n)
    random_hours = rng.choice(24, size=n, p=HOUR_RISK)
    random_mins  = rng.integers(0, 60, n)
    timestamps   = [
        start + timedelta(days=int(d), hours=int(h), minutes=int(m))
        for d, h, m in zip(random_days, random_hours, random_mins)
    ]

    # States (weighted)
    state_names   = list(STATE_WEIGHTS.keys())
    state_probs = np.array(list(STATE_WEIGHTS.values()))
    state_probs = state_probs / state_probs.sum()
    states = rng.choice(state_names, size=n, p=state_probs)
    
    districts = [
        rng.choice(DISTRICTS[s]) for s in states
    ]

    # Road type (NHs are riskier)
    road_probs = [0.35, 0.25, 0.18, 0.14, 0.08]
    road_types = rng.choice(ROAD_TYPES, size=n, p=road_probs)

    # Cause (over-speeding dominates)
    cause_probs = [0.35, 0.12, 0.10, 0.10, 0.08, 0.08, 0.06, 0.05, 0.04, 0.02]
    causes      = rng.choice(CAUSES, size=n, p=cause_probs)

    # Vehicles involved
    vehicles_involved = rng.choice(VEHICLE_TYPES, size=n)
    num_vehicles      = rng.integers(1, 5, size=n)

    # Casualties (correlated with road type & cause)
    base_fatal  = np.where(road_types == "National Highway", 0.18, 0.10)
    base_fatal  = np.where(causes == "Drunk Driving",  base_fatal + 0.08, base_fatal)
    base_fatal  = np.where(causes == "Over Speeding",  base_fatal + 0.05, base_fatal)
    fatal_flags = rng.random(n) < base_fatal
    fatalities  = np.where(fatal_flags, rng.integers(1, 5, n), 0)
    injuries    = rng.integers(0, 8, n) + np.where(fatal_flags, 0, rng.integers(1, 4, n))

    severity = np.where(fatalities > 0, "Fatal",
               np.where(injuries > 2, "Grievous", "Minor"))

    # Weather
    weather   = rng.choice(WEATHER_COND, size=n, p=[0.60, 0.20, 0.10, 0.07, 0.03])
    road_surf = rng.choice(ROAD_SURFACE, size=n, p=[0.55, 0.25, 0.12, 0.08])
    collision = rng.choice(COLLISION_TYPES, size=n)

    # Coordinates (rough bounding boxes per state)
    STATE_BBOX = {
        "Uttar Pradesh":  (23.9, 30.4, 77.0, 84.6),
        "Tamil Nadu":     (8.1,  13.6, 76.2, 80.3),
        "Maharashtra":    (15.6, 22.0, 72.6, 80.9),
        "Madhya Pradesh": (21.1, 26.9, 74.0, 82.8),
        "Karnataka":      (11.6, 18.5, 74.0, 78.5),
        "Rajasthan":      (23.0, 30.2, 69.5, 78.3),
        "Andhra Pradesh": (12.4, 19.9, 76.8, 84.6),
        "Gujarat":        (20.1, 24.7, 68.2, 74.5),
        "West Bengal":    (21.6, 27.2, 85.8, 89.9),
        "Telangana":      (15.8, 19.9, 77.2, 81.3),
        "Bihar":          (24.3, 27.5, 83.3, 88.3),
        "Kerala":         (8.3,  12.8, 74.9, 77.4),
        "Haryana":        (27.7, 30.9, 74.5, 77.6),
        "Punjab":         (29.5, 32.5, 73.9, 76.9),
        "Delhi":          (28.4, 28.9, 76.8, 77.4),
        "Odisha":         (17.8, 22.6, 81.4, 87.5),
    }
    lats, lons = [], []
    for s in states:
        lat_min, lat_max, lon_min, lon_max = STATE_BBOX[s]
        lats.append(rng.uniform(lat_min, lat_max))
        lons.append(rng.uniform(lon_min, lon_max))

    df = pd.DataFrame({
        "accident_id":        [f"ACC{i:07d}" for i in range(1, n + 1)],
        "datetime":           timestamps,
        "state":              states,
        "district":           districts,
        "road_type":          road_types,
        "cause":              causes,
        "vehicle_type":       vehicles_involved,
        "num_vehicles":       num_vehicles,
        "fatalities":         fatalities,
        "injuries":           injuries,
        "severity":           severity,
        "weather":            weather,
        "road_surface":       road_surf,
        "collision_type":     collision,
        "latitude":           np.round(lats, 4),
        "longitude":          np.round(lons, 4),
    })

    df["datetime"] = pd.to_datetime(df["datetime"])
    df["year"]     = df["datetime"].dt.year
    df["month"]    = df["datetime"].dt.month
    df["hour"]     = df["datetime"].dt.hour
    df["weekday"]  = df["datetime"].dt.day_name()
    df["is_night"] = df["hour"].apply(lambda h: "Night" if (h < 6 or h >= 20) else "Day")

    logger.success(f"Generated {len(df):,} records across {df['state'].nunique()} states.")
    return df


def save_to_sqlite(df: pd.DataFrame, db_path: Path) -> None:
    """Load dataframe into SQLite database."""
    logger.info(f"Saving to SQLite: {db_path}")
    conn = sqlite3.connect(db_path)
    df.to_sql("accidents", conn, if_exists="replace", index=False)

    # Create useful indexes
    conn.execute("CREATE INDEX IF NOT EXISTS idx_state    ON accidents(state)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_year     ON accidents(year)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_severity ON accidents(severity)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hour     ON accidents(hour)")
    conn.commit()
    conn.close()
    logger.success("SQLite database ready.")


def main():
    logger.info("=== India Traffic Accident — Data Ingestion ===")

    out_csv = RAW_DIR / "accidents.csv"
    if out_csv.exists():
        logger.info(f"Raw data already exists at {out_csv}. Skipping generation.")
        df = pd.read_csv(out_csv, parse_dates=["datetime"])
    else:
        df = generate_synthetic_data(n=50_000)
        df.to_csv(out_csv, index=False)
        logger.success(f"Raw data saved → {out_csv}")

    save_to_sqlite(df, DB_PATH)
    logger.success("Ingestion complete. Run scripts/clean.py next.")


if __name__ == "__main__":
    main()
