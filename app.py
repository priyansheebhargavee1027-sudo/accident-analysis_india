"""
dashboard/app.py
----------------
Streamlit interactive dashboard for India Traffic Accident Analysis.
Run: streamlit run dashboard/app.py
"""

import json
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parent.parent
DB_PATH  = ROOT / "data" / "accidents.db"
PROC_DIR = ROOT / "data" / "processed"
KPI_PATH = PROC_DIR / "kpis.json"

st.set_page_config(
    page_title  = "🚦 India Traffic Accident Analysis",
    page_icon   = "🚦",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

    .kpi-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #e94560;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        color: white;
    }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #e94560; }
    .kpi-label { font-size: 0.85rem; color: #aaa; margin-top: 0.25rem; }

    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e94560;
        border-left: 4px solid #e94560;
        padding-left: 0.75rem;
        margin: 1.5rem 0 1rem 0;
    }
    .stSelectbox label, .stMultiSelect label { color: #ccc !important; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    if not DB_PATH.exists():
        st.error("Database not found. Run: python scripts/ingest.py && python scripts/clean.py && python scripts/analyze.py")
        st.stop()
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("SELECT * FROM accidents_clean", conn, parse_dates=["datetime"])
    conn.close()
    return df


@st.cache_data
def load_kpis():
    if KPI_PATH.exists():
        with open(KPI_PATH) as f:
            return json.load(f)
    return {}


PLOTLY_DARK = dict(
    template      = "plotly_dark",
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(0,0,0,0)",
    font_color    = "#ccc",
)

ACCENT = "#e94560"
COLORS = px.colors.qualitative.Bold


# ── Sidebar ───────────────────────────────────────────────────────────────────

def sidebar_filters(df):
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg", width=80)
    st.sidebar.title("🚦 Filters")

    years = sorted(df["year"].unique())
    sel_years = st.sidebar.multiselect("Year", years, default=years)

    states = sorted(df["state"].unique())
    sel_states = st.sidebar.multiselect("State", states, default=states)

    road_types = sorted(df["road_type"].unique())
    sel_roads = st.sidebar.multiselect("Road Type", road_types, default=road_types)

    severity = sorted(df["severity"].unique())
    sel_sev = st.sidebar.multiselect("Severity", severity, default=severity)

    st.sidebar.markdown("---")
    st.sidebar.caption("Data: MoRTH / data.gov.in (Synthetic sample)")
    st.sidebar.caption("Dashboard built with Streamlit + Plotly")

    mask = (
        df["year"].isin(sel_years) &
        df["state"].isin(sel_states) &
        df["road_type"].isin(sel_roads) &
        df["severity"].isin(sel_sev)
    )
    return df[mask]


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_overview(df, kpis):
    st.title("🚦 India Traffic Accident Analysis")
    st.caption(f"Showing {len(df):,} records | Use sidebar to filter")

    # KPI Row
    cols = st.columns(5)
    kpi_defs = [
        (f"{len(df):,}",                        "Total Accidents"),
        (f"{df['fatalities'].sum():,}",          "Total Fatalities"),
        (f"{df['injuries'].sum():,}",            "Total Injuries"),
        (f"{df['fatalities'].sum()/len(df)*100:.1f}%", "Fatality Rate"),
        (f"{(df['is_night']=='Night').mean()*100:.1f}%", "Night Accidents"),
    ]
    for col, (val, label) in zip(cols, kpi_defs):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    # Yearly trend
    with c1:
        st.markdown('<div class="section-header">📈 Yearly Trend</div>', unsafe_allow_html=True)
        yr = df.groupby("year").agg(accidents=("accident_id","count"), fatalities=("fatalities","sum")).reset_index()
        fig = go.Figure()
        fig.add_bar(x=yr["year"], y=yr["accidents"], name="Accidents", marker_color=ACCENT)
        fig.add_scatter(x=yr["year"], y=yr["fatalities"], name="Fatalities",
                        line=dict(color="#00d2ff", width=2), yaxis="y2")
        fig.update_layout(
            **PLOTLY_DARK,
            yaxis2=dict(overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.1),
            xaxis_title="Year", yaxis_title="Accidents",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Severity pie
    with c2:
        st.markdown('<div class="section-header">🔴 Severity Distribution</div>', unsafe_allow_html=True)
        sev = df["severity"].value_counts().reset_index()
        sev.columns = ["Severity", "Count"]
        fig = px.pie(sev, values="Count", names="Severity",
                     color_discrete_map={"Fatal":"#e94560","Grievous":"#f5a623","Minor":"#4ecdc4"},
                     hole=0.45)
        fig.update_layout(**PLOTLY_DARK)
        st.plotly_chart(fig, use_container_width=True)


def page_hotspots(df):
    st.title("🗺️ Hotspot Analysis")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Top States by Accidents</div>', unsafe_allow_html=True)
        top = df.groupby("state").size().nlargest(10).reset_index(name="accidents")
        fig = px.bar(top, x="accidents", y="state", orientation="h",
                     color="accidents", color_continuous_scale="Reds")
        fig.update_layout(**PLOTLY_DARK, yaxis=dict(autorange="reversed"),
                          coloraxis_showscale=False, xaxis_title="Accidents", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">Fatality Rate by State (Top 10)</div>', unsafe_allow_html=True)
        fat = df.groupby("state").agg(
            accidents=("accident_id","count"),
            fatalities=("fatalities","sum")
        ).reset_index()
        fat["fatality_rate"] = fat["fatalities"] / fat["accidents"] * 100
        fat = fat.nlargest(10, "fatality_rate")
        fig = px.bar(fat, x="fatality_rate", y="state", orientation="h",
                     color="fatality_rate", color_continuous_scale="OrRd")
        fig.update_layout(**PLOTLY_DARK, yaxis=dict(autorange="reversed"),
                          coloraxis_showscale=False, xaxis_title="Fatality Rate (%)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    # Road type
    st.markdown('<div class="section-header">Road Type Risk Matrix</div>', unsafe_allow_html=True)
    rt = df.groupby("road_type").agg(
        accidents=("accident_id","count"),
        fatalities=("fatalities","sum"),
    ).reset_index()
    rt["fatality_rate"] = rt["fatalities"] / rt["accidents"] * 100
    fig = px.scatter(rt, x="accidents", y="fatality_rate", size="fatalities",
                     color="road_type", text="road_type",
                     labels={"accidents":"Total Accidents","fatality_rate":"Fatality Rate (%)"},
                     color_discrete_sequence=COLORS)
    fig.update_traces(textposition="top center")
    fig.update_layout(**PLOTLY_DARK, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Map
    st.markdown('<div class="section-header">📍 Accident Density Map (Sample)</div>', unsafe_allow_html=True)
    sample = df.sample(min(3000, len(df)), random_state=42)
    fig = px.scatter_mapbox(
        sample, lat="latitude", lon="longitude",
        color="severity", size_max=8, opacity=0.5,
        color_discrete_map={"Fatal":"red","Grievous":"orange","Minor":"yellow"},
        zoom=4, center={"lat": 22, "lon": 80},
        mapbox_style="carto-darkmatter",
        hover_data=["state","district","cause","road_type"],
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500,
                      paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


def page_time(df):
    st.title("⏰ Time-Based Pattern Analysis")

    # Hour distribution
    st.markdown('<div class="section-header">Accidents by Hour of Day</div>', unsafe_allow_html=True)
    hourly = df.groupby("hour").agg(
        accidents=("accident_id","count"),
        fatalities=("fatalities","sum")
    ).reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=hourly["hour"], y=hourly["accidents"], name="Accidents",
                marker_color=ACCENT, secondary_y=False)
    fig.add_scatter(x=hourly["hour"], y=hourly["fatalities"], name="Fatalities",
                    line=dict(color="#00d2ff", width=2), secondary_y=True)
    fig.update_layout(**PLOTLY_DARK, xaxis=dict(dtick=1, title="Hour of Day"),
                      yaxis_title="Accidents", yaxis2_title="Fatalities",
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Day vs Night</div>', unsafe_allow_html=True)
        dn = df.groupby("is_night").agg(
            accidents=("accident_id","count"),
            fatalities=("fatalities","sum")
        ).reset_index()
        dn["fatality_rate"] = dn["fatalities"] / dn["accidents"] * 100
        fig = go.Figure(data=[
            go.Bar(name="Accidents",    x=dn["is_night"], y=dn["accidents"],    marker_color="#e94560"),
            go.Bar(name="Fatalities",   x=dn["is_night"], y=dn["fatalities"],   marker_color="#f5a623"),
        ])
        fig.update_layout(**PLOTLY_DARK, barmode="group", xaxis_title="Time of Day")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">Monthly Pattern</div>', unsafe_allow_html=True)
        mon = df.groupby(["month","month_name"]).size().reset_index(name="accidents")
        mon = mon.sort_values("month")
        fig = px.line(mon, x="month_name", y="accidents", markers=True,
                      color_discrete_sequence=[ACCENT])
        fig.update_layout(**PLOTLY_DARK, xaxis_title="Month", yaxis_title="Accidents")
        st.plotly_chart(fig, use_container_width=True)

    # Weekday heatmap
    st.markdown('<div class="section-header">Weekday × Hour Accident Heatmap</div>', unsafe_allow_html=True)
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heat = df.groupby(["weekday","hour"]).size().reset_index(name="accidents")
    heat_pivot = heat.pivot(index="weekday", columns="hour", values="accidents").reindex(day_order)
    fig = px.imshow(heat_pivot, color_continuous_scale="Reds",
                    labels=dict(x="Hour of Day", y="", color="Accidents"))
    fig.update_layout(**PLOTLY_DARK, height=350)
    st.plotly_chart(fig, use_container_width=True)


def page_causes(df):
    st.title("🔍 Cause & Vehicle Analysis")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Top Accident Causes</div>', unsafe_allow_html=True)
        cause = df.groupby("cause").agg(
            accidents=("accident_id","count"),
            fatalities=("fatalities","sum")
        ).sort_values("fatalities", ascending=False).reset_index()
        fig = px.bar(cause, x="fatalities", y="cause", orientation="h",
                     color="accidents", color_continuous_scale="Reds")
        fig.update_layout(**PLOTLY_DARK, yaxis=dict(autorange="reversed"),
                          coloraxis_showscale=False, xaxis_title="Fatalities", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">Vehicle Type Distribution</div>', unsafe_allow_html=True)
        veh = df["vehicle_type"].value_counts().reset_index()
        veh.columns = ["Vehicle", "Count"]
        fig = px.pie(veh, values="Count", names="Vehicle", hole=0.4,
                     color_discrete_sequence=COLORS)
        fig.update_layout(**PLOTLY_DARK)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-header">Collision Type vs Fatalities</div>', unsafe_allow_html=True)
        col = df.groupby("collision_type").agg(
            accidents=("accident_id","count"),
            fatalities=("fatalities","sum")
        ).reset_index().sort_values("fatalities", ascending=False)
        fig = px.bar(col, x="collision_type", y=["accidents","fatalities"],
                     barmode="group", color_discrete_map={"accidents":ACCENT,"fatalities":"#4ecdc4"})
        fig.update_layout(**PLOTLY_DARK, xaxis_title="", legend_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown('<div class="section-header">Weather Impact</div>', unsafe_allow_html=True)
        wx = df.groupby("weather").agg(
            accidents=("accident_id","count"),
            fatalities=("fatalities","sum")
        ).reset_index()
        wx["fatality_rate"] = wx["fatalities"] / wx["accidents"] * 100
        fig = px.bar(wx, x="weather", y="fatality_rate",
                     color="fatality_rate", color_continuous_scale="Reds",
                     text=wx["fatality_rate"].round(1))
        fig.update_layout(**PLOTLY_DARK, coloraxis_showscale=False,
                          xaxis_title="Weather Condition", yaxis_title="Fatality Rate (%)")
        st.plotly_chart(fig, use_container_width=True)


def page_data(df):
    st.title("📋 Raw Data Explorer")
    st.caption(f"{len(df):,} records match current filters")

    cols = ["accident_id","datetime","state","district","road_type",
            "cause","severity","fatalities","injuries","hour","is_night","weather"]
    st.dataframe(df[cols].head(500), use_container_width=True, height=450)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Filtered CSV", csv,
                       "filtered_accidents.csv", "text/csv")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    df   = load_data()
    kpis = load_kpis()
    df   = sidebar_filters(df)

    pages = {
        "📊 Overview":         lambda: page_overview(df, kpis),
        "🗺️ Hotspots":         lambda: page_hotspots(df),
        "⏰ Time Patterns":    lambda: page_time(df),
        "🔍 Causes & Vehicles":lambda: page_causes(df),
        "📋 Data Explorer":    lambda: page_data(df),
    }

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate", list(pages.keys()))
    pages[page]()


if __name__ == "__main__":
    main()
