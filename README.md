# 🚦 India Traffic Accident Data Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> A full-stack data analysis project to uncover accident hotspots, time-based risk patterns, and safety insights across Indian roads using open government data.

---

## 📌 Project Overview

This project analyzes India's road accident data (sourced from MoRTH / data.gov.in) to:

- 🗺️ Identify **geographic hotspots** (state, district, road type)
- 🕐 Detect **time-based patterns** (night vs. day, weekday vs. weekend, monthly trends)
- 📊 Visualize **severity & cause distributions**
- 🧠 Generate **actionable safety recommendations**

---

## 🗂️ Project Structure

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

## 📦 Data Sources

| Source | Description | URL |
|--------|-------------|-----|
| MoRTH Annual Report | State/district-wise accident stats | [morth.nic.in](https://morth.nic.in) |
| data.gov.in | Open government accident datasets | [data.gov.in](https://data.gov.in) |
| NCRB | Crime & accident records | [ncrb.gov.in](https://ncrb.gov.in) |
| OSM / Google Maps API | Road geometry for hotspot mapping | Optional |

> **Note:** Synthetic sample data is included in `data/raw/` for immediate testing without API keys.

---

## 🚀 Quick Start

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

## 📊 Key Analyses

### 🗺️ Hotspot Detection
- Top 10 states & districts by accident frequency
- Road-type risk scoring (NH, SH, MDR, Urban)
- Folium choropleth maps

### ⏰ Time-Based Patterns
- Hour-of-day accident distribution
- Day vs. Night severity comparison
- Monthly & seasonal trends
- Weekday vs. weekend heatmaps

### 🔍 Cause Analysis
- Top accident causes (overspeeding, drunk driving, road conditions)
- Fatality rate by cause
- Vehicle type breakdown

### 💡 Safety Recommendations
- Automated risk scoring per state
- Evidence-based intervention suggestions

---

## 🖥️ Dashboard (Streamlit)

The interactive dashboard includes:
- KPI cards (total accidents, fatalities, fatality rate)
- Interactive choropleth map
- Time-series charts
- Filterable data tables
- Downloadable reports

---

## 🛠️ Tech Stack

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

## 📈 Power BI Integration

Processed data is exported to `data/processed/powerbi_export.csv` — ready to import directly into Power BI for enterprise dashboards.

See `reports/powerbi_guide.md` for step-by-step setup.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/new-analysis`
3. Commit changes: `git commit -m 'Add seasonal trend analysis'`
4. Push & open a Pull Request

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- Ministry of Road Transport & Highways (MoRTH), India
- National Crime Records Bureau (NCRB)
- Open Data Initiative, data.gov.in
