#  India Traffic Accident Data Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> A full-stack data analysis project to uncover accident hotspots, time-based risk patterns, and safety insights across Indian roads using open government data.

---

##  Project Overview

This project analyzes India's road accident data (sourced from MoRTH / data.gov.in) to:

-  Identify **geographic hotspots** (state, district, road type)
-  Detect **time-based patterns** (night vs. day, weekday vs. weekend, monthly trends)
-  Visualize **severity & cause distributions**
-  Generate **actionable safety recommendations**

---

##  Project Structure

```
india-traffic-accidents/
├── data/
│   ├── raw/                    # Original downloaded datasets (CSV/XLSX)
│   └── processed/              # Cleaned & transformed data
├── sql/
│   ├── schema.sql              # SQLite/PostgreSQL schema
│   └── queries.sql             # Key analytical queries
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_hotspot_analysis.ipynb
│   ├── 04_time_analysis.ipynb
│   └── 05_recommendations.ipynb
├── scripts/
│   ├── ingest.py               # Download & load data
│   ├── clean.py                # Data cleaning pipeline
│   ├── analyze.py              # Core analysis engine
│   └── visualize.py            # Chart generation
├── dashboard/
│   └── app.py                  # Streamlit interactive dashboard
├── reports/
│   └── summary_report.md       # Auto-generated insights
├── requirements.txt
├── .env.example
└── README.md
```

---

##  Data Sources

| Source | Description | URL |
|--------|-------------|-----|
| MoRTH Annual Report | State/district-wise accident stats | [morth.nic.in](https://morth.nic.in) |
| data.gov.in | Open government accident datasets | [data.gov.in](https://data.gov.in) |
| NCRB | Crime & accident records | [ncrb.gov.in](https://ncrb.gov.in) |
| OSM / Google Maps API | Road geometry for hotspot mapping | Optional |

> **Note:** Synthetic sample data is included in `data/raw/` for immediate testing without API keys.

---

##  Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/india-traffic-accidents.git
cd india-traffic-accidents
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Pipeline
```bash
# Step 1: Ingest & generate sample data
python scripts/ingest.py

# Step 2: Clean the data
python scripts/clean.py

# Step 3: Run analysis
python scripts/analyze.py

# Step 4: Launch dashboard
streamlit run dashboard/app.py
```

### 3. Explore Notebooks
```bash
jupyter lab notebooks/
```

---

##  Key Analyses

###  Hotspot Detection
- Top 10 states & districts by accident frequency
- Road-type risk scoring (NH, SH, MDR, Urban)
- Folium choropleth maps

###  Time-Based Patterns
- Hour-of-day accident distribution
- Day vs. Night severity comparison
- Monthly & seasonal trends
- Weekday vs. weekend heatmaps

###  Cause Analysis
- Top accident causes (overspeeding, drunk driving, road conditions)
- Fatality rate by cause
- Vehicle type breakdown

###  Safety Recommendations
- Automated risk scoring per state
- Evidence-based intervention suggestions

---

##  Dashboard (Streamlit)

The interactive dashboard includes:
- KPI cards (total accidents, fatalities, fatality rate)
- Interactive choropleth map
- Time-series charts
- Filterable data tables
- Downloadable reports

---

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Visualization | Plotly, Folium, Seaborn, Matplotlib |
| Dashboard | Streamlit |
| Notebooks | Jupyter Lab |
| BI Export | Power BI compatible CSV/JSON output |

---

##  Power BI Integration

Processed data is exported to `data/processed/powerbi_export.csv` — ready to import directly into Power BI for enterprise dashboards.

See `reports/powerbi_guide.md` for step-by-step setup.

---

##  Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/new-analysis`
3. Commit changes: `git commit -m 'Add seasonal trend analysis'`
4. Push & open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

##  Acknowledgements

- Ministry of Road Transport & Highways (MoRTH), India
- National Crime Records Bureau (NCRB)
- Open Data Initiative, data.gov.in

##  How to Run

```bash
python3 -m pip install -r requirements.txt
python3 scripts/ingest.py
python3 scripts/clean.py
python3 scripts/analyze.py
streamlit run dashboard/app.py





## India Traffic Accident Data Analysis

This project started with a simple question:
**why do certain roads in India see more accidents than others?**

I used publicly available data (MoRTH, data.gov.in, NCRB) and built a small pipeline + dashboard to explore patterns like time of accidents, road types, and major causes.

---

## Why I Built This

Most analyses I found online were very surface-level (just totals by state).
I wanted to go deeper — especially into **time patterns, road types, and severity trends**.

---

## What This Project Does

* Finds **accident-heavy regions** (state/district level)
* Analyzes **time patterns** (hour, day, month)
* Looks at **major causes** (overspeeding, road conditions, etc.)
* Builds a **simple dashboard** to explore everything interactively

---

## Key Insights

* Accidents peak during **evening hours (around 6–9 PM)**
* **National Highways** tend to have higher fatality rates
* **Overspeeding** is the most common cause across datasets
* Weekend nights show slightly higher severity in some regions

---

## Project Structure (roughly)

```
india-traffic-accidents/
├── data/              # raw + cleaned datasets
├── scripts/           # ingestion, cleaning, analysis
├── notebooks/         # exploration + experiments
├── dashboard/         # streamlit app (main output)
├── reports/           # generated summaries
```

---

## How to Run

```bash
python3 -m pip install -r requirements.txt

python3 scripts/ingest.py
python3 scripts/clean.py
python3 scripts/analyze.py

streamlit run dashboard/app.py
```

---

## Tools I Used

* Python (Pandas, NumPy)
* Plotly, Matplotlib (visuals)
* Streamlit (dashboard)
* SQLite (basic storage)

---

## Dashboard

The Streamlit app shows:

* Total accidents, fatalities, fatality rate
* Time-based trends
* Region-wise comparisons
* Interactive charts

---

## Notes

* Some datasets are incomplete, so results are indicative, not perfect
* Synthetic sample data is included for quick testing

---

## Future Improvements

* Add prediction model (accident risk scoring)
* Improve data cleaning (handling missing district-level data)
* Better map visualizations (geo-level accuracy)

---

## About

Built as a data analysis project while preparing for data roles.
Still improving it as I learn more.

