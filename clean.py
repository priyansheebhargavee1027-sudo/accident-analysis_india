"""
scripts/clean.py
----------------
Cleans raw accident data and writes processed output.
Produces: data/processed/accidents_clean.csv
          data/processed/powerbi_export.csv
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger

ROOT      = Path(__file__).resolve().parent.parent
RAW_CSV   = ROOT / "data" / "raw" / "accidents.csv"
PROC_DIR  = ROOT / "data" / "processed"
DB_PATH   = ROOT / "data" / "accidents.db"
PROC_DIR.mkdir(parents=True, exist_ok=True)


def load_raw() -> pd.DataFrame:
    logger.info(f"Loading raw data from {RAW_CSV}")
    df = pd.read_csv(RAW_CSV, parse_dates=["datetime"])
    logger.info(f"Loaded {len(df):,} rows × {df.shape[1]} columns")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning data…")
    original_len = len(df)

    # 1. Drop exact duplicates
    df = df.drop_duplicates(subset="accident_id")

    # 2. Ensure numeric cols are non-negative
    for col in ["fatalities", "injuries", "num_vehicles"]:
        df[col] = df[col].clip(lower=0)

    # 3. Standardise string columns
    str_cols = ["state", "district", "road_type", "cause",
                "vehicle_type", "weather", "road_surface",
                "collision_type", "severity", "weekday", "is_night"]
    for col in str_cols:
        df[col] = df[col].str.strip().str.title()

    # 4. Re-derive time features (robust)
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.dropna(subset=["datetime"])
    df["year"]    = df["datetime"].dt.year
    df["month"]   = df["datetime"].dt.month
    df["hour"]    = df["datetime"].dt.hour
    df["weekday"] = df["datetime"].dt.day_name()
    df["quarter"] = df["datetime"].dt.quarter
    df["is_night"] = df["hour"].apply(
        lambda h: "Night" if (h < 6 or h >= 20) else "Day"
    )

    # 5. Derived: fatality rate, total casualties
    df["total_casualties"] = df["fatalities"] + df["injuries"]
    df["is_fatal"]         = (df["fatalities"] > 0).astype(int)

    # 6. Month name
    month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                 7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    df["month_name"] = df["month"].map(month_map)

    # 7. Day period
    def day_period(h):
        if 6 <= h < 12:  return "Morning"
        if 12 <= h < 17: return "Afternoon"
        if 17 <= h < 20: return "Evening"
        return "Night"
    df["day_period"] = df["hour"].apply(day_period)

    # 8. Weekend flag
    df["is_weekend"] = df["weekday"].isin(["Saturday", "Sunday"]).astype(int)

    dropped = original_len - len(df)
    logger.info(f"Dropped {dropped:,} rows. Clean dataset: {len(df):,} rows")
    return df.reset_index(drop=True)


def compute_state_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregated state-level risk metrics."""
    summary = df.groupby("state").agg(
        total_accidents =("accident_id", "count"),
        total_fatalities=("fatalities", "sum"),
        total_injuries  =("injuries",   "sum"),
        fatal_accidents =("is_fatal",   "sum"),
    ).reset_index()
    summary["fatality_rate_pct"] = (
        summary["total_fatalities"] / summary["total_accidents"] * 100
    ).round(2)
    summary["risk_score"] = (
        0.5 * (summary["total_accidents"]  / summary["total_accidents"].max()) +
        0.5 * (summary["fatality_rate_pct"] / summary["fatality_rate_pct"].max())
    ).round(3)
    summary = summary.sort_values("total_accidents", ascending=False)
    return summary


def save_outputs(df: pd.DataFrame, state_summary: pd.DataFrame) -> None:
    # Cleaned full dataset
    clean_path = PROC_DIR / "accidents_clean.csv"
    df.to_csv(clean_path, index=False)
    logger.success(f"Cleaned data → {clean_path}")

    # State summary
    state_path = PROC_DIR / "state_summary.csv"
    state_summary.to_csv(state_path, index=False)
    logger.success(f"State summary → {state_path}")

    # Power BI export (flattened, Excel-friendly column names)
    pbi = df[[
        "accident_id", "datetime", "year", "month", "month_name",
        "hour", "day_period", "is_night", "weekday", "is_weekend",
        "state", "district", "latitude", "longitude",
        "road_type", "cause", "vehicle_type", "collision_type",
        "weather", "road_surface", "severity",
        "fatalities", "injuries", "total_casualties", "is_fatal",
    ]].copy()
    pbi.to_csv(PROC_DIR / "powerbi_export.csv", index=False)
    logger.success("Power BI export → data/processed/powerbi_export.csv")

    # Update SQLite with clean data
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("accidents_clean", conn, if_exists="replace", index=False)
    state_summary.to_sql("state_summary", conn, if_exists="replace", index=False)
    conn.close()
    logger.success("SQLite updated with cleaned tables.")


def main():
    logger.info("=== India Traffic Accident — Data Cleaning ===")
    df = load_raw()
    df = clean(df)
    state_summary = compute_state_summary(df)
    save_outputs(df, state_summary)
    logger.success("Cleaning complete. Run scripts/analyze.py next.")


if __name__ == "__main__":
    main()
