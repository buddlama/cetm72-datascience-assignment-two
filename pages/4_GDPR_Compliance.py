# pages/4_GDPR_Compliance.py

import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.data import load_data, apply_filters, render_summary_metrics, DATA_PATH, SUBJECTS_AFFECTED_ORDER
from utils.charts import (
    plot_gdpr_compliance,
    plot_gdpr_compliance_by_category,
    plot_gdpr_compliance_by_decision,
    plot_gdpr_compliance_by_subjects_affected,
    plot_gdpr_dumbbell_by_decision,
)

st.set_page_config(page_title="GDPR Compliance — Q1 2024", layout="wide")

df_incidents, df_rows = load_data(DATA_PATH)

st.title("GDPR Compliance")
st.caption("Which sectors are reporting breaches within the legally required 72-hour window?")

# ─────────────────────────────────────────────────────────────────────────
# Page-scoped filters
# ─────────────────────────────────────────────────────────────────────────

st.sidebar.header("Filters")

selected_sectors = st.sidebar.multiselect(
    "Sector", options=sorted(df_incidents["sector"].unique())
)
selected_categories = st.sidebar.multiselect(
    "Incident Category", options=sorted(df_incidents["category"].unique())
)

filtered_df = apply_filters(
    df_incidents,
    sectors=selected_sectors,
    categories=selected_categories,
)

# ─────────────────────────────────────────────────────────────────────────
# Summary metrics
# ─────────────────────────────────────────────────────────────────────────

render_summary_metrics(filtered_df, df_incidents)

st.divider()



if len(filtered_df) == 0:
    st.warning("No incidents match the current filter selection.")
else:
    st.plotly_chart(plot_gdpr_compliance(filtered_df), use_container_width=True)

    st.caption(f"Showing {len(filtered_df):,} of {len(df_incidents):,} total incidents.")

    st.divider()

    st.markdown("#### Does Incident Category Affect Compliance?")
    st.caption(
        "Tests whether non-cyber (human error) incidents, already shown to "
        "dominate by volume, are also slower to report."
    )
    st.plotly_chart(plot_gdpr_compliance_by_category(filtered_df), use_container_width=True)

    st.divider()

    # st.markdown("#### Does Regulatory Outcome Relate to Reporting Speed?")
    # st.caption(
    #     "Tests whether incidents resulting in formal ICO action were also "
    #     "more likely to be reported late."
    # )
    # st.plotly_chart(plot_gdpr_compliance_by_decision(filtered_df), use_container_width=True)

    st.divider()

    st.markdown("#### Compliance Gap by Regulatory Decision — Absolute Counts")
    st.caption(
        "Each row shows compliant (●) vs non-compliant (●) incident counts joined by a line. "
        "Line length is the absolute gap — a 60% rate on 2,000 incidents is a very different "
        "story from 60% on 50 incidents."
    )
    st.plotly_chart(plot_gdpr_dumbbell_by_decision(filtered_df), use_container_width=True)

    # st.divider()

    # st.markdown("#### Does Breach Scale Relate to Reporting Speed?")
    # st.caption(
    #     "Tests whether larger breaches (more people affected) are reported "
    #     "more slowly than smaller ones."
    # )
    # st.plotly_chart(
    #     plot_gdpr_compliance_by_subjects_affected(filtered_df, SUBJECTS_AFFECTED_ORDER),
    #     use_container_width=True,
    # )
