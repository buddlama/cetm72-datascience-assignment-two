import streamlit as st

st.set_page_config(
    page_title="UK Data Security Incidents Dashboard",
    page_icon="🔒",
    layout="wide",
)

st.title("UK Data Security Incidents Dashboard")
st.subheader("Q1 2024 — ICO Data Security Incident Trends")

st.markdown(
    """
    This dashboard has been developed as part of a data visualisation prototype
    exploring personal data breach reports received by the Information
    Commissioner's Office (ICO) during Q1 2024 (January–March).

    The dashboard is built for two audiences: junior government officials
    requiring a clear, self-service overview of breach trends, and data
    journalists seeking evidence-based insight into UK data security incidents.
    """
)

st.divider()

st.markdown("### Contents")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        **📋 Narrative**
        A written summary of the key Q1 2024 findings — what happened, which
        sectors were most affected, and where GDPR compliance gaps exist.
        """
    )
    st.markdown(
        """
        **📊 Incident Types**
        Breakdown of how breaches occurred — human error versus sophisticated
        cyber-attacks — filterable by sector and category.
        """
    )

with col2:
    st.markdown(
        """
        **🏢 Sectoral Vulnerability**
        Which sectors report the most incidents, and how each splits between
        cyber and non-cyber causes.
        """
    )
    st.markdown(
        """
        **⏱️ GDPR Compliance**
        Which sectors are reporting within the legally required 72-hour window
        — and which are falling behind.
        """
    )

st.divider()

st.caption(
    "Data source: ICO Data Security Incident Trends. "
    "Use the sidebar to navigate between pages. Each page has its own "
    "filters scoped to the question it answers."
)
