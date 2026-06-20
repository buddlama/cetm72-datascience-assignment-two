# app.py
# CETM25 Assignment 2 — ICO Data Security Incidents Dashboard (Q1 2024)
# Run with: streamlit run app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ─────────────────────────────────────────────────────────────────────────
# DATA LOADING (cached so it only runs once, not on every interaction)
# ─────────────────────────────────────────────────────────────────────────

@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath)

    df = df.rename(columns={
        "BI Reference":               "bi_ref",
        "Year":                       "year",
        "Quarter":                    "quarter",
        "Data Subject Type":          "subject_type",
        "Data Type":                  "data_type",
        "Decision Taken":             "decision",
        "Incident Category":          "category",
        "Incident Type":              "incident_type",
        "No. Data Subjects Affected": "subjects_affected",
        "Sector":                     "sector",
        "Time Taken to Report":       "time_to_report"
    })

    # Filter to Q1 2024 only — must run after rename so column names match
    df = df[(df["year"] == 2024) & (df["quarter"] == "Qtr 1")].reset_index(drop=True)

    # Strip whitespace from text columns (covers both "string" and "object" dtype)
    str_cols = df.select_dtypes(include=["string", "object"]).columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    # GDPR compliance flag — True if reported within 72 hours
    compliant_bands = ["Less than 24 hours", "24 hours to 72 hours"]
    df["gdpr_compliant"] = df["time_to_report"].isin(compliant_bands)

    # df_rows: full dataset — for Data Type / Data Subject Type analysis (not used in filters yet)
    df_rows = df.copy()

    # df_incidents: one row per incident — used by all three charts and all filters
    df_incidents = df.drop_duplicates(subset=["bi_ref"]).reset_index(drop=True)

    return df_incidents, df_rows


# ─────────────────────────────────────────────────────────────────────────
# FILTERING
# ─────────────────────────────────────────────────────────────────────────

def apply_filters(df_incidents, sectors=None, incident_types=None, categories=None, report_times=None):
    """
    Filters df_incidents by Sector, Incident Type, Incident Category, and
    Time Taken to Report — the four fields specified in the Assignment 1
    interactivity design.

    NOTE: Data Type is deliberately excluded from filtering. df_incidents
    is deduplicated to one row per BI Reference and only retains the FIRST
    data_type value per incident, so filtering on it here would give
    misleading results for incidents that exposed multiple data types.
    """
    df = df_incidents.copy()

    if sectors:
        df = df[df["sector"].isin(sectors)]
    if incident_types:
        df = df[df["incident_type"].isin(incident_types)]
    if categories:
        df = df[df["category"].isin(categories)]
    if report_times:
        df = df[df["time_to_report"].isin(report_times)]

    return df


# ─────────────────────────────────────────────────────────────────────────
# CHART 1 — Incident Type Breakdown
# ─────────────────────────────────────────────────────────────────────────


def incident_type_counts(df_incidents):
    counts = df_incidents["incident_type"].value_counts().reset_index()
    counts.columns = ["incident_type", "count"]
    return counts


def plot_incident_type_breakdown(df_incidents, highlight_top_n=1):
    counts = incident_type_counts(df_incidents)
    counts = counts.sort_values("count", ascending=True).reset_index(drop=True)

    GREY = "#B0B0B0"
    ACCENT = "#D55E00"

    n = len(counts)
    colours = [GREY] * n
    for i in range(max(0, n - highlight_top_n), n):
        colours[i] = ACCENT

    fig = go.Figure(
        go.Bar(
            x=counts["count"],
            y=counts["incident_type"],
            orientation="h",
            marker_color=colours,
            text=counts["count"],
            textposition="outside",
        )
    )

    if n > 0:
        top_label = counts.iloc[-1]["incident_type"]
        top_value = counts.iloc[-1]["count"]
        total = counts["count"].sum()
        top_pct = (top_value / total) * 100 if total > 0 else 0
        title_text = (
            f"'{top_label}' Is the Leading Incident Type<br>"
            f"<sub>Accounts for {top_pct:.0f}% of filtered incidents (n={total})</sub>"
        )
    else:
        title_text = "No incidents match the current filters"

    fig.update_layout(
        title={"text": title_text, "x": 0.0, "xanchor": "left"},
        xaxis_title="Number of Incidents",
        yaxis_title=None,
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        showlegend=False,
        margin=dict(l=10, r=40, t=90, b=40),
        height=600,
    )

    return fig

#line chart shwoing cyber attack and non cyber attack over time
def plot_incident_type_trend(df_incidents):
    df_incidents['date'] = pd.to_datetime(df_incidents['year'].astype(str) + '-' + df_incidents['quarter'].str.extract(r'Qtr (\d)')[0].astype(int).apply(lambda x: (x-1)*3+1).astype(str) + '-01')
    counts = df_incidents.groupby(['date', 'category']).size().reset_index(name='count')

    fig = px.line(counts, x='date', y='count', color='category', markers=True,
                  labels={'date': 'Date', 'count': 'Number of Incidents', 'category': 'Incident Category'},
                  title='Incident Type Trend Over Time')

    fig.update_layout(
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        margin=dict(l=10, r=40, t=90, b=40),
        height=600,
    )

    return fig


# ─────────────────────────────────────────────────────────────────────────
# CHART 2 — Sectoral Vulnerability
# ─────────────────────────────────────────────────────────────────────────

def sector_category_counts(df_incidents):
    counts = (
        df_incidents
        .groupby(["sector", "category"])
        .size()
        .reset_index(name="count")
    )
    return counts


def sector_order(df_incidents):
    totals = (
        df_incidents
        .groupby("sector")
        .size()
        .reset_index(name="total")
        .sort_values("total", ascending=True)
    )
    return totals["sector"].tolist()


def plot_sectoral_vulnerability(df_incidents):
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=700)
        return fig

    counts = sector_category_counts(df_incidents)
    order = sector_order(df_incidents)

    colour_map = {
        "Cyber": "#D55E00",
        "Non Cyber": "#0072B2",
    }

    fig = px.bar(
        counts,
        x="count",
        y="sector",
        color="category",
        orientation="h",
        category_orders={"sector": order},
        color_discrete_map=colour_map,
        labels={"count": "Number of Incidents", "sector": "Sector", "category": "Incident Category"},
    )

    fig.update_layout(
        title="Sectoral Breach Volume — Filtered View",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        legend_title_text="",
        margin=dict(l=10, r=40, t=80, b=40),
        height=700,
    )

    return fig


# ─────────────────────────────────────────────────────────────────────────
# CHART 3 — GDPR Compliance by Sector
# ─────────────────────────────────────────────────────────────────────────

def gdpr_compliance_by_sector(df_incidents):
    summary = (
        df_incidents
        .groupby("sector")["gdpr_compliant"]
        .agg(total="count", compliant="sum")
        .reset_index()
    )
    summary["compliance_pct"] = (summary["compliant"] / summary["total"]) * 100
    return summary


def plot_gdpr_compliance(df_incidents):
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=700)
        return fig

    summary = gdpr_compliance_by_sector(df_incidents)
    summary = summary.sort_values("compliance_pct", ascending=True).reset_index(drop=True)

    GREY = "#B0B0B0"
    ACCENT = "#D55E00"

    n = len(summary)
    colours = [GREY] * n
    colours[0] = ACCENT

    labels = [
        f"{row.compliance_pct:.0f}%  (n={row.total})"
        for row in summary.itertuples()
    ]

    fig = go.Figure(
        go.Bar(
            x=summary["compliance_pct"],
            y=summary["sector"],
            orientation="h",
            marker_color=colours,
            text=labels,
            textposition="outside",
        )
    )

    worst_sector = summary.iloc[0]["sector"]
    worst_pct = summary.iloc[0]["compliance_pct"]
    overall_pct = (df_incidents["gdpr_compliant"].sum() / len(df_incidents)) * 100

    fig.update_layout(
        title={
            "text": f"{worst_sector} Lags Furthest Behind on GDPR 72-Hour Reporting<br>"
                    f"<sub>Just {worst_pct:.0f}% reported within the legal window (filtered view)</sub>",
            "x": 0.0,
            "xanchor": "left",
        },
        xaxis_title="% Reported Within 72 Hours",
        yaxis_title=None,
        xaxis=dict(range=[0, 110], showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=10, r=40, t=90, b=40),
        height=700,
    )

    fig.add_vline(
        x=overall_pct,
        line_dash="dash",
        line_color="black",
        annotation_text=f"Filtered avg: {overall_pct:.0f}%",
        annotation_position="top",
    )

    return fig


# ─────────────────────────────────────────────────────────────────────────
# STREAMLIT APP LAYOUT
# ─────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="ICO Data Security Incidents — Q1 2024", layout="wide")

st.title("UK Data Security Incidents — Q1 2024")
st.markdown(
    "Interactive dashboard built on ICO Data Security Incident Trends data. "
    "Filter using the sidebar to explore incidents by sector, type, category, and reporting time."
)

# Load data once, cached
df_incidents, df_rows = load_data("ico-dataset.csv")

# --- Sidebar filters ---
st.sidebar.header("Filters")

selected_sectors = st.sidebar.multiselect(
    "Sector",
    options=sorted(df_incidents["sector"].unique())
)

selected_incident_types = st.sidebar.multiselect(
    "Incident Type",
    options=sorted(df_incidents["incident_type"].unique())
)

selected_categories = st.sidebar.multiselect(
    "Incident Category",
    options=sorted(df_incidents["category"].unique())
)

selected_report_times = st.sidebar.multiselect(
    "Time Taken to Report",
    options=sorted(df_incidents["time_to_report"].unique())
)

# --- Apply filters ---
filtered_df = apply_filters(
    df_incidents,
    sectors=selected_sectors,
    incident_types=selected_incident_types,
    categories=selected_categories,
    report_times=selected_report_times,
)

# --- Headline stats ---
total_filtered = len(filtered_df)
total_all = len(df_incidents)

col1, col2, col3 = st.columns(3)
col1.metric("Incidents (filtered)", f"{total_filtered:,}", f"of {total_all:,} total")

if total_filtered > 0:
    non_cyber_pct = (filtered_df["category"] == "Non Cyber").mean() * 100
    compliant_pct = filtered_df["gdpr_compliant"].mean() * 100
else:
    non_cyber_pct = 0
    compliant_pct = 0

col2.metric("Non-Cyber Incidents", f"{non_cyber_pct:.0f}%")
col3.metric("GDPR Compliant", f"{compliant_pct:.0f}%")

st.divider()

# --- Charts ---
if total_filtered == 0:
    st.warning("No incidents match the current filter selection. Try removing one or more filters.")
else:
    st.plotly_chart(plot_incident_type_breakdown(filtered_df), use_container_width=True)
    st.plotly_chart(plot_sectoral_vulnerability(filtered_df), use_container_width=True)
    st.plotly_chart(plot_gdpr_compliance(filtered_df), use_container_width=True)