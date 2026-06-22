import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.data import load_data_with_spinner


df_incidents, df_rows = load_data_with_spinner()

total = len(df_incidents)
non_cyber = (df_incidents["category"] == "Non Cyber").sum()
non_cyber_pct = (non_cyber / total) * 100
cyber_pct = 100 - non_cyber_pct

top_incident = df_incidents["incident_type"].value_counts().idxmax()
top_incident_count = df_incidents["incident_type"].value_counts().max()
top_incident_pct = (top_incident_count / total) * 100

top_sector = df_incidents["sector"].value_counts().idxmax()
top_sector_count = df_incidents["sector"].value_counts().max()
top_sector_pct = (top_sector_count / total) * 100

compliant_pct = df_incidents["gdpr_compliant"].mean() * 100
non_compliant_pct = 100 - compliant_pct

sector_compliance = (
    df_incidents.groupby("sector")["gdpr_compliant"].mean() * 100
).sort_values()
worst_sector = sector_compliance.index[0]
worst_sector_pct = sector_compliance.iloc[0]


st.title("Narrative")
st.caption("Description of key Q1 2024 trends")

st.markdown(
    f"""
    ### Data security incident trends for Q1 2024 (1st January 2024 to 31st March 2024)

    In Q1 2024, there were **{total:,} incidents** reported to the ICO.

    The majority of incidents reported were **non-cyber incidents**
    (see definition in glossary document), making up **{non_cyber_pct:.0f}%**
    of the total, while cyber incidents accounted for the remaining
    **{cyber_pct:.0f}%**.

    **{top_incident}** was the most common incident type reported, making up
    **{top_incident_pct:.0f}%** of incidents reported in Q1 2024.

    **{top_sector}** was the most common sector for incidents, making up
    **{top_sector_pct:.0f}%** of the total reported in Q1 2024.

    **{compliant_pct:.0f}%** of incidents reported in Q1 2024 were reported
    within 72 hours of discovery, as required under GDPR Article 33. The
    remaining **{non_compliant_pct:.0f}%** fell outside the legally required
    reporting window. **{worst_sector}** had the lowest compliance rate of
    any sector, at just **{worst_sector_pct:.0f}%**.
    """
)

st.divider()

st.markdown(
    """
    #### Methodology and limitations

    The data in this dashboard is drawn from ICO records of data security
    incidents reported between 1st January and 31st March 2024. Each incident
    is recorded once (deduplicated by BI Reference); where an incident exposed
    multiple data types, the additional records are retained separately for
    data-type-level analysis but are not double-counted in incident totals.

    Percentage changes derived from sectors with a small number of total
    incidents should be treated with caution, as a single case can shift the
    percentage significantly. Sample sizes are shown alongside percentages
    throughout this dashboard where relevant.
    """
)
