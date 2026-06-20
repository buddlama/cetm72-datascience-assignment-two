# utils/data.py
# Shared data loading and filtering logic, imported by every page.

import streamlit as st
import pandas as pd


def render_summary_metrics(filtered_df, df_incidents):
    """
    Renders the standard three-metric header row used on every chart page:
    filtered incident count, non-cyber %, GDPR compliant %.
    Reacts to whatever filters are currently applied on that page.
    """
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

    # df_incidents: one row per incident — used by all charts and all filters
    df_incidents = df.drop_duplicates(subset=["bi_ref"]).reset_index(drop=True)

    return df_incidents, df_rows


def apply_filters(df_incidents, sectors=None, incident_types=None, categories=None, report_times=None):
    """
    Filters df_incidents by Sector, Incident Type, Incident Category, and
    Time Taken to Report.

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


DATA_PATH = "ico-dataset.csv"

# Canonical band order for subjects_affected — this column is ordinal but
# does not sort correctly alphabetically or by appearance order (see D-15).
# Any chart using this column must apply this explicit order.
SUBJECTS_AFFECTED_ORDER = ["1 to 9", "10 to 99", "100 to 1k", "1k to 10k", "10k to 100k"]
