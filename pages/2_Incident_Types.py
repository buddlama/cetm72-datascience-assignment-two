import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.data import load_data, apply_filters, render_summary_metrics, DATA_PATH
from utils.charts import (
    plot_incident_type_by_category,
    plot_breach_scale_by_category,
)

st.set_page_config(page_title="Incident Types — Q1 2024", layout="wide")

df_incidents, df_rows = load_data(DATA_PATH)

st.title("Incident Types")
st.caption("How did Q1 2024 breaches happen — human error or cyber-attack?")

st.sidebar.header("Filters")

selected_sectors = st.sidebar.multiselect(
    "Sector", options=sorted(df_incidents["sector"].unique())
)
selected_categories = st.sidebar.multiselect(
    "Incident Category", options=sorted(df_incidents["category"].unique())
)
selected_report_times = st.sidebar.multiselect(
    "Time Taken to Report", options=sorted(df_incidents["time_to_report"].unique())
)

filtered_df = apply_filters(
    df_incidents,
    sectors=selected_sectors,
    categories=selected_categories,
    report_times=selected_report_times,
)

render_summary_metrics(filtered_df, df_incidents)

st.divider()

if len(filtered_df) == 0:
    st.warning("No incidents match the current filter selection.")
else:
    st.plotly_chart(plot_incident_type_by_category(filtered_df), use_container_width=True)
    
    st.caption(f"Showing {len(filtered_df):,} of {len(df_incidents):,} total incidents.")

    st.divider()

    st.subheader("How Many People Were Affected?")
    st.caption(
        "Proportion of incidents within each category falling into each breach-scale band. "
        "Normalised to % so the two categories (very different in volume) can be compared fairly."
    )
    st.plotly_chart(plot_breach_scale_by_category(filtered_df), use_container_width=True)
