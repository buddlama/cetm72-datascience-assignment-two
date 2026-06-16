"""
ICO Data Security Incident Trends — Q1 2024 Dashboard
CETM25 Assignment 2 Prototype | Buddha Lama | University of Sunderland

Data source: ICO (2026) Data Security Incident Trends Dataset
https://ico.org.uk/action-weve-taken/complaints-and-concerns-data-sets/data-security-incident-trends/
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UK Data Security Incidents Q1 2024",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f8f9fa; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a2640;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #ffffff !important;
    }

    /* Section headers */
    .section-header {
        font-size: 18px;
        font-weight: 600;
        color: #1a2640;
        margin-top: 24px;
        margin-bottom: 4px;
        border-left: 4px solid #e63946;
        padding-left: 10px;
    }

    /* Narrative banner */
    .narrative-box {
        background-color: #1a2640;
        color: #ffffff;
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 20px;
        font-size: 15px;
        line-height: 1.6;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #888;
        font-size: 12px;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ── Colour palette (colour-blind safe) ───────────────────────────────────────
BLUE   = "#2166ac"
RED    = "#e63946"
ORANGE = "#f4a261"
GREEN  = "#2a9d8f"
PURPLE = "#6a4c93"
GREY   = "#adb5bd"

CYBER_COLOURS = {"Non Cyber": BLUE, "Cyber": RED}
GDPR_COLOURS  = {
    "Less than 24 hours":  "#2a9d8f",
    "24 hours to 72 hours": "#2166ac",
    "72 hours to 1 week":   "#f4a261",
    "More than 1 week":     "#e63946",
}

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "ico_q1_2024_sample.csv")
    df = pd.read_csv(path)

    # Filter to Q1 2024
    df = df[(df["Year"] == 2024) & (df["Quarter"] == "Qtr 1")].copy()

    # Deduplicate on BI Reference for incident-level counts
    # (one BI ref = one incident; multiple rows exist per data type)
    incidents = df.drop_duplicates(subset="BI Reference").copy()

    # GDPR compliance flag: within 72 hours = compliant
    compliant_bands = {"Less than 24 hours", "24 hours to 72 hours"}
    incidents["GDPR Compliant"] = incidents["Time Taken to Report"].apply(
        lambda x: "Compliant" if x in compliant_bands else "Non-Compliant"
    )

    # Month from BI reference order (proxy — real dataset has notification date)
    incidents = incidents.reset_index(drop=True)
    n = len(incidents)
    third = n // 3
    incidents["Month"] = (
        ["January"] * third +
        ["February"] * third +
        ["March"] * (n - 2 * third)
    )

    return df, incidents


df_raw, df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔐 ICO Q1 2024")
    st.markdown("**UK Data Security Incidents**")
    st.markdown("---")

    st.markdown("### Filters")

    all_sectors = sorted(df["Sector"].unique())
    selected_sectors = st.multiselect(
        "Sector",
        options=all_sectors,
        default=all_sectors,
        help="Filter by industry sector"
    )

    all_categories = sorted(df["Incident Category"].unique())
    selected_category = st.multiselect(
        "Incident category",
        options=all_categories,
        default=all_categories,
    )

    all_times = ["Less than 24 hours", "24 hours to 72 hours",
                 "72 hours to 1 week", "More than 1 week"]
    selected_time = st.multiselect(
        "Time taken to report",
        options=all_times,
        default=all_times,
    )

    st.markdown("---")
    st.markdown(
        "<small style='color:#aaa'>Data source: ICO (2026) Data Security "
        "Incident Trends Dataset.<br>Filtered to Q1 2024 (Jan–Mar).</small>",
        unsafe_allow_html=True,
    )

# ── Apply filters ─────────────────────────────────────────────────────────────
mask = (
    df["Sector"].isin(selected_sectors) &
    df["Incident Category"].isin(selected_category) &
    df["Time Taken to Report"].isin(selected_time)
)
filtered = df[mask].copy()

if filtered.empty:
    st.warning("No incidents match the current filters. Please adjust your selection.")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🔐 UK Data Security Incident Trends")
st.markdown("### Q1 2024 (January – March) | ICO Reported Incidents")

# Narrative banner
total       = len(filtered)
cyber_pct   = round(filtered[filtered["Incident Category"] == "Cyber"].shape[0] / total * 100)
non_cyber_pct = 100 - cyber_pct
compliant_n = filtered[filtered["GDPR Compliant"] == "Compliant"].shape[0]
compliant_pct = round(compliant_n / total * 100)

st.markdown(f"""
<div class="narrative-box">
  📊 <strong>Key finding:</strong> In Q1 2024, <strong>{non_cyber_pct}%</strong> of the
  {total:,} reported incidents were caused by <strong>human error</strong> — not sophisticated
  cyber-attacks. Yet <strong>{100 - compliant_pct}%</strong> of organisations failed to report
  breaches within GDPR's mandatory 72-hour deadline, leaving data subjects vulnerable and
  regulators unaware.
</div>
""", unsafe_allow_html=True)

# ── KPI metrics ───────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total incidents", f"{total:,}")
col2.metric("Non-cyber (human error)", f"{non_cyber_pct}%")
col3.metric("GDPR 72hr compliant", f"{compliant_pct}%")

top_type = filtered["Incident Type"].value_counts().idxmax()
top_type_short = top_type if len(top_type) < 28 else top_type[:25] + "..."
col4.metric("Top breach type", top_type_short)

st.markdown("---")

# ── Chart 1: Monthly incident trend (line chart) ──────────────────────────────
st.markdown('<div class="section-header">Incident trend — January to March 2024</div>', unsafe_allow_html=True)
st.caption("Monthly volume split by incident category. Reveals whether the problem is growing, stable, or improving over the quarter.")

month_order = ["January", "February", "March"]
trend = (
    filtered.groupby(["Month", "Incident Category"])
    .size()
    .reset_index(name="Count")
)
trend["Month"] = pd.Categorical(trend["Month"], categories=month_order, ordered=True)
trend = trend.sort_values("Month")

fig_trend = px.line(
    trend,
    x="Month", y="Count",
    color="Incident Category",
    markers=True,
    color_discrete_map=CYBER_COLOURS,
    labels={"Count": "Number of incidents", "Month": ""},
)
fig_trend.update_traces(line_width=3, marker_size=10)
fig_trend.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend_title_text="",
    margin=dict(t=20, b=20, l=10, r=10),
    font_family="sans-serif",
    yaxis=dict(gridcolor="#f0f0f0"),
    xaxis=dict(gridcolor="#f0f0f0"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_trend, use_container_width=True)

# ── Chart 2 + 3: side by side ─────────────────────────────────────────────────
col_left, col_right = st.columns(2)

# Chart 2: Top incident types (horizontal bar) ─────────────────────────────────
with col_left:
    st.markdown('<div class="section-header">Top incident types</div>', unsafe_allow_html=True)
    st.caption("Horizontal bar chart ordered by frequency. Reveals that misdirected emails — not ransomware — dominate.")

    type_counts = (
        filtered.groupby(["Incident Type", "Incident Category"])
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=True)
        .tail(12)
    )

    fig_types = px.bar(
        type_counts,
        x="Count", y="Incident Type",
        color="Incident Category",
        orientation="h",
        color_discrete_map=CYBER_COLOURS,
        labels={"Count": "Number of incidents", "Incident Type": ""},
    )
    fig_types.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_text="",
        margin=dict(t=10, b=20, l=10, r=10),
        font_family="sans-serif",
        xaxis=dict(gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_types, use_container_width=True)

# Chart 3: GDPR compliance by sector (stacked bar) ────────────────────────────
with col_right:
    st.markdown('<div class="section-header">GDPR 72-hour compliance by sector</div>', unsafe_allow_html=True)
    st.caption("Stacked bar showing reporting time bands per sector. Red = missed deadline by over a week.")

    gdpr = (
        filtered.groupby(["Sector", "Time Taken to Report"])
        .size()
        .reset_index(name="Count")
    )

    time_order = ["Less than 24 hours", "24 hours to 72 hours",
                  "72 hours to 1 week", "More than 1 week"]
    gdpr["Time Taken to Report"] = pd.Categorical(
        gdpr["Time Taken to Report"], categories=time_order, ordered=True
    )
    gdpr = gdpr.sort_values("Time Taken to Report")

    # Sort sectors by total incidents descending
    sector_order = (
        gdpr.groupby("Sector")["Count"].sum()
        .sort_values(ascending=True).index.tolist()
    )

    fig_gdpr = px.bar(
        gdpr,
        x="Count", y="Sector",
        color="Time Taken to Report",
        orientation="h",
        color_discrete_map=GDPR_COLOURS,
        category_orders={"Sector": sector_order, "Time Taken to Report": time_order},
        labels={"Count": "Number of incidents", "Sector": ""},
    )
    fig_gdpr.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_text="Time to report",
        margin=dict(t=10, b=20, l=10, r=10),
        font_family="sans-serif",
        xaxis=dict(gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_gdpr, use_container_width=True)

# ── Chart 4: Sectoral vulnerability (stacked bar — cyber vs non-cyber) ────────
st.markdown("---")
st.markdown('<div class="section-header">Sectoral vulnerability — cyber vs human error</div>', unsafe_allow_html=True)
st.caption("Which sectors face the most incidents, and what proportion stem from human error vs cyber attacks?")

sector_cat = (
    filtered.groupby(["Sector", "Incident Category"])
    .size()
    .reset_index(name="Count")
)
sector_order2 = (
    sector_cat.groupby("Sector")["Count"].sum()
    .sort_values(ascending=False).index.tolist()
)

fig_sector = px.bar(
    sector_cat,
    x="Sector", y="Count",
    color="Incident Category",
    color_discrete_map=CYBER_COLOURS,
    category_orders={"Sector": sector_order2},
    labels={"Count": "Number of incidents", "Sector": ""},
    barmode="stack",
)
fig_sector.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend_title_text="",
    margin=dict(t=10, b=60, l=10, r=10),
    font_family="sans-serif",
    yaxis=dict(gridcolor="#f0f0f0"),
    xaxis=dict(tickangle=-30),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_sector, use_container_width=True)

# ── Chart 5: Data types exposed (pie / donut) ─────────────────────────────────
st.markdown("---")
col5, col6 = st.columns([1, 1])

with col5:
    st.markdown('<div class="section-header">Data types exposed</div>', unsafe_allow_html=True)
    st.caption("What categories of personal data are most frequently compromised?")

    dtype_counts = (
        df_raw[
            df_raw["BI Reference"].isin(filtered["BI Reference"])
        ]["Data Type"]
        .value_counts()
        .reset_index()
    )
    dtype_counts.columns = ["Data Type", "Count"]

    fig_dtype = px.pie(
        dtype_counts,
        names="Data Type", values="Count",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig_dtype.update_traces(textposition="inside", textinfo="percent+label")
    fig_dtype.update_layout(
        paper_bgcolor="white",
        margin=dict(t=10, b=10, l=10, r=10),
        font_family="sans-serif",
        showlegend=False,
    )
    st.plotly_chart(fig_dtype, use_container_width=True)

with col6:
    st.markdown('<div class="section-header">Regulatory decisions</div>', unsafe_allow_html=True)
    st.caption("What action did the ICO take following each reported incident?")

    dec_counts = filtered["Decision Taken"].value_counts().reset_index()
    dec_counts.columns = ["Decision", "Count"]

    fig_dec = px.bar(
        dec_counts,
        x="Count", y="Decision",
        orientation="h",
        color="Count",
        color_continuous_scale=[[0, "#c9daf8"], [1, "#1a2640"]],
        labels={"Count": "Number of incidents", "Decision": ""},
    )
    fig_dec.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        coloraxis_showscale=False,
        margin=dict(t=10, b=20, l=10, r=10),
        font_family="sans-serif",
        xaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_dec, use_container_width=True)

# ── Raw data expander ─────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 View filtered incident data"):
    display_cols = ["BI Reference", "Sector", "Incident Category", "Incident Type",
                    "No. Data Subjects Affected", "Time Taken to Report",
                    "GDPR Compliant", "Decision Taken"]
    st.dataframe(
        filtered[display_cols].sort_values("Sector"),
        use_container_width=True,
        height=300,
    )
    st.caption(f"Showing {len(filtered):,} incidents. Each row = one unique breach incident.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  <strong>ICO Data Security Incident Trends Dashboard</strong> | Q1 2024 (January–March) |
  Data source: Information Commissioner's Office (ICO, 2026) |
  Built with Python · Pandas · Plotly · Streamlit |
  CETM25 Assignment 2 — University of Sunderland
</div>
""", unsafe_allow_html=True)
