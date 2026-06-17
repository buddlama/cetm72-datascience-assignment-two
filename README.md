# ICO Data Security Dashboard — Vibe Coding Guide
**CETM25 Assignment 2 | Buddha Lama | University of Sunderland**

---

## What you are building

An interactive Streamlit dashboard that visualises UK data security incidents
reported to the ICO (Information Commissioner's Office) for Q1 2024
(January to March 2024).

The dashboard must communicate one central finding:

> "In Q1 2024, the biggest threat to UK data security was not sophisticated
> cyber-attacks but human error — yet a significant proportion of organisations
> failed to report breaches within GDPR's mandatory 72-hour deadline."

Two audiences will use it:
- **Junior government officials** — deploy and operate it. No coding knowledge.
  Must be usable within 5 minutes of opening a URL, no installation needed.
- **Data journalists** — read the charts and use the findings in news reporting.

---

## How to use this guide

Work through the phases in order. Do not jump ahead.

Each phase ends with a **STOP AND CHECK** section. Before moving to the next
phase, complete every check and write down what you observed. These observations
are your evidence for the System Testing section of your assignment report.

When something breaks or behaves unexpectedly — good. That is the point.
Write down what happened and how you fixed it. That is your methodology.

---

## Before you start — one-time setup

Open your terminal. Navigate to where you want to create the project.

```bash
# Create the project folder
mkdir ico_dashboard
cd ico_dashboard

# Create a virtual environment (keeps your packages isolated)
python3 -m venv venv

# Activate it — you must do this every time you open a new terminal
source venv/bin/activate        # Mac or Linux
venv\Scripts\activate           # Windows

# You should now see (venv) at the start of your terminal prompt
# That means the environment is active

# Install the required packages
pip install streamlit pandas plotly numpy

# Create the requirements file so others can install the same packages
pip freeze > requirements.txt
```

Download the real ICO dataset:
1. Go to: `https://ico.org.uk/action-weve-taken/complaints-and-concerns-data-sets/data-security-incident-trends/`
2. Download the full dataset (Excel or CSV format)
3. Save it inside your `ico_dashboard` folder as `ico_raw.csv`

Create three empty Python files:
```bash
touch data.py
touch charts.py
touch app.py
```

Your folder should now look like this:
```
ico_dashboard/
├── venv/               ← virtual environment (do not edit)
├── data.py             ← you will build this in Phase 1 and 2
├── charts.py           ← you will build this in Phase 3
├── app.py              ← you will build this in Phase 4
├── ico_raw.csv         ← the real ICO dataset
└── requirements.txt    ← auto-generated
```

---

## Phase 1 — Understand the data before touching it

**Goal:** Load the raw file, print what is in it, and understand its structure
before writing any processing logic. Do not filter or clean anything yet.

Open `data.py` and write the following. Run it after each print statement
so you see the output one step at a time.

```python
import pandas as pd

# Load the raw file
df = pd.read_csv("ico_raw.csv")

# Step 1: How big is it?
print("=== RAW FILE ===")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print()

# Step 2: What are the exact column names?
print("=== COLUMN NAMES ===")
for col in df.columns:
    print(f"  '{col}'")
print()

# Step 3: What does a sample row look like?
print("=== FIRST 3 ROWS ===")
print(df.head(3).to_string())
print()

# Step 4: What years and quarters exist?
print("=== YEAR VALUES ===")
print(df["Year"].value_counts().sort_index())
print()
print("=== QUARTER VALUES ===")
print(df["Quarter"].value_counts())
print()

# Step 5: What are the Incident Category values?
# This is important — the values are "Non Cyber" and "Cyber" with a space
print("=== INCIDENT CATEGORY VALUES ===")
print(df["Incident Category"].value_counts())
print()

# Step 6: What are the Time Taken to Report values?
print("=== TIME TAKEN TO REPORT VALUES ===")
print(df["Time Taken to Report"].value_counts())
print()
```

Run it:
```bash
python3 data.py
```

---

### STOP AND CHECK — Phase 1

Write down the answers to these questions before continuing.
These go in your System Testing section.

```
[ ] What is the exact total row count of the raw file?
    Answer: _______________

[ ] Are the column names exactly as listed in this guide?
    If any differ, note the actual names — use those in your code.
    Answer: _______________

[ ] What is the exact string for Incident Category?
    Is it "Non Cyber" or "Non-Cyber" or something else?
    Answer: _______________

[ ] What quarter string format does the data use?
    Is it "Qtr 1" or "Q1" or "Quarter 1"?
    Answer: _______________

[ ] Does a Notification Date column exist?
    Answer: Yes / No
```

**Common issue here:** The column names in the real ICO dataset sometimes have
trailing spaces or slightly different capitalisation than expected. If your code
throws a KeyError, run `print(df.columns.tolist())` and copy the exact names.

---

## Phase 2 — Build the preprocessing pipeline

**Goal:** Filter the data to Q1 2024, deduplicate incidents, create the GDPR
compliance flag. Build this as a function that returns two dataframes.

**The key concept to understand:**
One incident (one `BI Reference`) appears on multiple rows — one row per data
type involved. For example, a single breach involving names, emails, and health
records creates three rows with the same BI Reference. If you count rows
directly you will overcount incidents by roughly 2-3x.

Add this to `data.py`, below your Phase 1 code:

```python
def load_and_prepare(filepath="ico_raw.csv"):
    """
    Loads and preprocesses the ICO dataset.
    Returns: df_incidents (one row per incident), df_raw (all rows, Q1 2024 only)
    """

    # --- LOAD ---
    df = pd.read_csv(filepath)
    print(f"[1] Raw rows loaded: {len(df)}")

    # --- FILTER TO Q1 2024 ---
    # Use the exact string values you confirmed in Phase 1
    df = df[(df["Year"] == 2024) & (df["Quarter"] == "Qtr 1")]
    print(f"[2] Rows after Q1 2024 filter: {len(df)}")

    # Store the filtered but not-yet-deduplicated version
    # This is needed for the Data Types chart (Chart 5)
    df_raw = df.copy()

    # --- DEDUPLICATE TO INCIDENT LEVEL ---
    # drop_duplicates keeps the first row for each BI Reference
    # This gives us one row per unique incident
    df_incidents = df.drop_duplicates(subset="BI Reference").copy()
    print(f"[3] Unique incidents after deduplication: {len(df_incidents)}")
    print(f"    Rows removed by deduplication: {len(df) - len(df_incidents)}")

    # --- NULL CHECK ---
    print("[4] Null values per column:")
    nulls = df_incidents.isnull().sum()
    for col, count in nulls.items():
        if count > 0:
            print(f"    {col}: {count} nulls")
    if nulls.sum() == 0:
        print("    No nulls found")

    # --- GDPR COMPLIANCE FLAG ---
    # Compliant = reported within 72 hours
    compliant_bands = {"Less than 24 hours", "24 hours to 72 hours"}
    df_incidents["GDPR Compliant"] = df_incidents["Time Taken to Report"].apply(
        lambda x: "Compliant" if x in compliant_bands else "Non-Compliant"
    )
    compliant_pct = (
        df_incidents["GDPR Compliant"].value_counts(normalize=True)["Compliant"] * 100
    )
    print(f"[5] GDPR compliance rate: {compliant_pct:.1f}%")
    print(f"    (ICO published benchmark for Q1 2024: ~62%)")

    # --- MONTH COLUMN ---
    # Use Notification Date if it exists, otherwise assign proportionally
    if "Notification Date" in df_incidents.columns:
        df_incidents["Notification Date"] = pd.to_datetime(
            df_incidents["Notification Date"], errors="coerce"
        )
        df_incidents["Month"] = df_incidents["Notification Date"].dt.strftime("%B")
    else:
        # Proportional fallback: split incidents across three months
        n = len(df_incidents)
        third = n // 3
        df_incidents = df_incidents.reset_index(drop=True)
        df_incidents["Month"] = (
            ["January"] * third +
            ["February"] * third +
            ["March"] * (n - 2 * third)
        )
    print("[6] Month column created")
    print(df_incidents["Month"].value_counts())

    # --- VERIFICATION CHECKS ---
    print("\n[7] Top 5 incident types:")
    print(df_incidents["Incident Type"].value_counts().head(5))

    print("\n[8] Top 5 sectors:")
    print(df_incidents["Sector"].value_counts().head(5))

    print("\n[9] Incident category split:")
    cats = df_incidents["Incident Category"].value_counts(normalize=True) * 100
    print(cats.round(1))

    return df_incidents, df_raw


# Run when this file is executed directly
if __name__ == "__main__":
    df_incidents, df_raw = load_and_prepare()
    print(f"\nReady: {len(df_incidents)} incidents, {len(df_raw)} raw rows")
```

Run it:
```bash
python3 data.py
```

---

### STOP AND CHECK — Phase 2

```
[ ] What is the unique incident count after deduplication?
    Answer: _______________

[ ] How many rows were removed by deduplication?
    Answer: _______________

[ ] Were any null values found? In which columns?
    Answer: _______________

[ ] What is your GDPR compliance rate?
    Is it near the ICO benchmark of ~62%? If not, why might it differ?
    Answer: _______________

[ ] What is the top incident type?
    Expected: something related to email or data sent to wrong recipient
    Actual: _______________

[ ] Is Health the highest-volume sector?
    Answer: Yes / No — actual top sector: _______________

[ ] What is the Non Cyber percentage?
    Expected: approximately 73%
    Actual: _______________
```

**Common issues here:**

If your compliance rate is very different from 62%, check whether the Time Taken
to Report values in your real data match the expected bands exactly.
Run `print(df["Time Taken to Report"].unique())` to see what is actually there.

If deduplication removes 0 rows, check that "BI Reference" is the exact column
name. If the column is named differently, update the subset parameter.

---

## Phase 3 — Build charts one at a time

**Goal:** Build each chart as a standalone function. Test each one individually
by calling it directly from `charts.py` before wiring it into the app.

**Rule:** Build one chart, run it, check it, fix any issues, then move to the
next. Do not write all six charts before testing any of them.

**Colour palette — copy this exactly, use nothing else:**

```python
CATEGORY_COLOURS = {
    "Non Cyber": "#2166ac",   # blue — human error
    "Cyber":     "#e63946",   # red — cyber attacks
}

TIME_COLOURS = {
    "Less than 24 hours":   "#2a9d8f",
    "24 hours to 72 hours": "#2166ac",
    "72 hours to 1 week":   "#f4a261",
    "More than 1 week":     "#e63946",
}
```

**Rules that apply to every chart:**
- All Y axes start at zero — no truncated baselines
- White plot background: `plot_bgcolor="white"`, `paper_bgcolor="white"`
- Light grey gridlines: `gridcolor="#f0f0f0"`
- Legend horizontal above chart: `legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)`
- No chart titles inside the figure — titles go in the Streamlit layout
- Plain English axis labels — not raw column names

Open `charts.py` and build each function below.

---

### Chart 1 — Monthly incident trend (line chart)

```python
import plotly.express as px
import pandas as pd

CATEGORY_COLOURS = {
    "Non Cyber": "#2166ac",
    "Cyber":     "#e63946",
}

TIME_COLOURS = {
    "Less than 24 hours":   "#2a9d8f",
    "24 hours to 72 hours": "#2166ac",
    "72 hours to 1 week":   "#f4a261",
    "More than 1 week":     "#e63946",
}

MONTH_ORDER = ["January", "February", "March"]


def chart_monthly_trend(df_incidents):
    trend = (
        df_incidents
        .groupby(["Month", "Incident Category"])
        .size()
        .reset_index(name="Count")
    )
    # Force correct month order
    trend["Month"] = pd.Categorical(
        trend["Month"], categories=MONTH_ORDER, ordered=True
    )
    trend = trend.sort_values("Month")

    fig = px.line(
        trend,
        x="Month", y="Count",
        color="Incident Category",
        markers=True,
        color_discrete_map=CATEGORY_COLOURS,
        labels={"Count": "Number of incidents", "Month": ""},
    )
    fig.update_traces(line_width=3, marker_size=10)
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        yaxis=dict(gridcolor="#f0f0f0", rangemode="tozero"),
        xaxis=dict(gridcolor="#f0f0f0"),
        margin=dict(t=30, b=20, l=10, r=10),
    )
    return fig
```

**Test Chart 1 by adding this at the bottom of charts.py and running it:**

```python
if __name__ == "__main__":
    from data import load_and_prepare
    df_incidents, df_raw = load_and_prepare()
    fig = chart_monthly_trend(df_incidents)
    fig.show()   # opens in your browser
```

```bash
python3 charts.py
```

**Check:**
```
[ ] Do three months appear on the X axis in the correct order?
[ ] Do both Non Cyber (blue) and Cyber (red) lines appear?
[ ] Does the Y axis start at zero?
[ ] If only one line appears — does your Month column have data in all three months?
```

---

### Chart 2 — Top incident types (horizontal bar)

Add to `charts.py`:

```python
def chart_incident_types(df_incidents):
    counts = (
        df_incidents
        .groupby(["Incident Type", "Incident Category"])
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=True)
        .tail(10)   # top 10 only
    )
    fig = px.bar(
        counts,
        x="Count", y="Incident Type",
        color="Incident Category",
        orientation="h",
        color_discrete_map=CATEGORY_COLOURS,
        labels={"Count": "Number of incidents", "Incident Type": ""},
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        xaxis=dict(gridcolor="#f0f0f0", rangemode="tozero"),
        margin=dict(t=30, b=20, l=10, r=10),
    )
    return fig
```

**Check:**
```
[ ] Is "Data emailed to incorrect recipient" (or similar) the top bar?
[ ] Is it clearly longer than Phishing and Ransomware bars?
[ ] Are Non Cyber bars blue and Cyber bars red?
[ ] Does the chart show 10 bars maximum?
```

**This chart delivers the counter-intuitive finding.** If ransomware appears
above email errors, check whether your deduplication is working correctly —
each incident should only be counted once.

---

### Chart 3 — GDPR compliance by sector (stacked horizontal bar)

Add to `charts.py`:

```python
def chart_gdpr_compliance(df_incidents):
    TIME_ORDER = [
        "Less than 24 hours",
        "24 hours to 72 hours",
        "72 hours to 1 week",
        "More than 1 week",
    ]
    gdpr = (
        df_incidents
        .groupby(["Sector", "Time Taken to Report"])
        .size()
        .reset_index(name="Count")
    )
    # Sector order: highest total incidents at top
    sector_order = (
        gdpr.groupby("Sector")["Count"].sum()
        .sort_values(ascending=True).index.tolist()
    )
    fig = px.bar(
        gdpr,
        x="Count", y="Sector",
        color="Time Taken to Report",
        orientation="h",
        color_discrete_map=TIME_COLOURS,
        category_orders={
            "Sector": sector_order,
            "Time Taken to Report": TIME_ORDER,
        },
        labels={"Count": "Number of incidents", "Sector": ""},
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        legend_title_text="Time to report",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        xaxis=dict(gridcolor="#f0f0f0", rangemode="tozero"),
        margin=dict(t=30, b=20, l=10, r=10),
    )
    return fig
```

**Check:**
```
[ ] Do all 4 time bands appear in the legend?
[ ] Are the colours in the correct order (teal → blue → amber → red)?
[ ] Does red ("More than 1 week") appear visibly in most sectors?
[ ] Is Health the longest bar (highest at top after sorting)?
```

---

### Chart 4 — Sectoral vulnerability (vertical stacked bar)

Add to `charts.py`:

```python
def chart_sector_vulnerability(df_incidents):
    sector_cat = (
        df_incidents
        .groupby(["Sector", "Incident Category"])
        .size()
        .reset_index(name="Count")
    )
    sector_order = (
        sector_cat.groupby("Sector")["Count"].sum()
        .sort_values(ascending=False).index.tolist()
    )
    fig = px.bar(
        sector_cat,
        x="Sector", y="Count",
        color="Incident Category",
        color_discrete_map=CATEGORY_COLOURS,
        category_orders={"Sector": sector_order},
        labels={"Count": "Number of incidents", "Sector": ""},
        barmode="stack",
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        yaxis=dict(gridcolor="#f0f0f0", rangemode="tozero"),
        xaxis=dict(tickangle=-30),
        margin=dict(t=30, b=80, l=10, r=10),
    )
    return fig
```

**Check:**
```
[ ] Is Health the tallest bar (leftmost after sorting)?
[ ] Is Non Cyber (blue) visually dominant in most bars?
[ ] Are sector labels readable — not cut off or overlapping?
[ ] Does the Y axis start at zero?
```

---

### Chart 5 — Data types exposed (donut chart)

**Important:** This chart uses `df_raw`, not `df_incidents`. One incident can
expose multiple data types — you want to count all of them, not just one per
incident. If you pass `df_incidents` here you will undercount.

Add to `charts.py`:

```python
import plotly.express as px

def chart_data_types(df_raw):
    # Confirm you are receiving df_raw, not df_incidents
    print(f"[chart_data_types] rows received: {len(df_raw)}")

    counts = (
        df_raw["Data Type"]
        .value_counts()
        .reset_index()
    )
    counts.columns = ["Data Type", "Count"]

    fig = px.pie(
        counts,
        names="Data Type",
        values="Count",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        paper_bgcolor="white",
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
    )
    return fig
```

**Check:**
```
[ ] Is "Basic personal identifiers" the largest slice?
[ ] Does the print statement confirm you received df_raw (more rows than df_incidents)?
[ ] Are all slices labelled with percentages?
[ ] Is there a visible hole in the centre (donut shape)?
```

---

### Chart 6 — Regulatory decisions (horizontal bar)

Add to `charts.py`:

```python
def chart_regulatory_decisions(df_incidents):
    counts = (
        df_incidents["Decision Taken"]
        .value_counts()
        .reset_index()
    )
    counts.columns = ["Decision", "Count"]
    counts = counts.sort_values("Count", ascending=True)

    fig = px.bar(
        counts,
        x="Count", y="Decision",
        orientation="h",
        color="Count",
        color_continuous_scale=[[0, "#c9daf8"], [1, "#1a2640"]],
        labels={"Count": "Number of incidents", "Decision": ""},
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#f0f0f0", rangemode="tozero"),
        margin=dict(t=30, b=20, l=10, r=10),
    )
    return fig
```

**Check:**
```
[ ] Is "No Further Action" the longest bar?
[ ] Are bars ordered shortest to longest (bottom to top)?
[ ] Does the sequential blue colour scale apply correctly?
```

---

### STOP AND CHECK — Phase 3

```
[ ] All 6 charts open in the browser when called individually?
[ ] Chart 2 shows email breach at top above ransomware/phishing?
[ ] Chart 5 receives df_raw — confirmed by the print statement row count?
[ ] Chart 3 shows all 4 time bands with correct colours?
[ ] No chart has a Y axis that starts above zero?

Write down any chart that broke and what the error was:
Issue: _______________
Fix: _______________
```

---

## Phase 4 — Build the Streamlit app

**Goal:** Wire everything together in `app.py`. The layout follows a specific
order — do not rearrange it. The sequence is:
**Perceive (KPIs) → Interpret (charts + filters) → Comprehend (full picture)**

This order follows Kirk's (2024) three-phase model for how audiences process
data visualisations. The journalist must see the headline finding first, then
use filters to explore, then reach a full conclusion by the end of the page.

Open `app.py` and build it in sections, running `streamlit run app.py` after
each section to check it renders before adding the next.

---

### Section A — Page config and data load

```python
import streamlit as st
import pandas as pd
from data import load_and_prepare
from charts import (
    chart_monthly_trend,
    chart_incident_types,
    chart_gdpr_compliance,
    chart_sector_vulnerability,
    chart_data_types,
    chart_regulatory_decisions,
)

st.set_page_config(
    page_title="UK Data Security Incidents Q1 2024",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def get_data():
    return load_and_prepare()

df_incidents, df_raw = get_data()
```

Run:
```bash
streamlit run app.py
```

You should see a blank wide-layout page with no errors. If you see an import
error, check that your function names in `charts.py` match exactly.

---

### Section B — Sidebar filters

Add below the data load:

```python
with st.sidebar:
    st.markdown("## 🔐 ICO Q1 2024")
    st.markdown("**UK Data Security Incidents**")
    st.markdown("---")
    st.markdown("### Filters")

    all_sectors = sorted(df_incidents["Sector"].dropna().unique())
    selected_sectors = st.multiselect(
        "Sector", options=all_sectors, default=all_sectors
    )

    all_categories = sorted(df_incidents["Incident Category"].dropna().unique())
    selected_categories = st.multiselect(
        "Incident category", options=all_categories, default=all_categories
    )

    all_times = [
        "Less than 24 hours",
        "24 hours to 72 hours",
        "72 hours to 1 week",
        "More than 1 week",
    ]
    selected_times = st.multiselect(
        "Time taken to report", options=all_times, default=all_times
    )

    st.markdown("---")
    st.markdown(
        "<small>Data: ICO (2026) Data Security Incident Trends</small>",
        unsafe_allow_html=True,
    )
```

**Test:** Deselect one sector. Does the sidebar update without error?

---

### Section C — Apply filters and guard clause

```python
# Apply filters to df_incidents
mask = (
    df_incidents["Sector"].isin(selected_sectors) &
    df_incidents["Incident Category"].isin(selected_categories) &
    df_incidents["Time Taken to Report"].isin(selected_times)
)
filtered = df_incidents[mask].copy()

# Apply matching filter to df_raw using BI Reference
filtered_raw = df_raw[
    df_raw["BI Reference"].isin(filtered["BI Reference"])
].copy()

# Guard clause — stop if no data matches the filters
if filtered.empty:
    st.warning(
        "No incidents match the current filters. "
        "Please adjust your selection in the sidebar."
    )
    st.stop()
```

**Test the guard clause:** Deselect everything in one filter. Does the warning
appear and prevent the charts from erroring?

---

### Section D — PERCEIVE (headline KPIs and narrative)

```python
# Page header
st.markdown("# 🔐 UK Data Security Incident Trends")
st.markdown("### Q1 2024 (January – March) | ICO Reported Incidents")

# Calculate dynamic values for narrative
total = len(filtered)
non_cyber_n = filtered[filtered["Incident Category"] == "Non Cyber"].shape[0]
non_cyber_pct = round(non_cyber_n / total * 100) if total > 0 else 0
compliant_n = filtered[filtered["GDPR Compliant"] == "Compliant"].shape[0]
non_compliant_pct = round((1 - compliant_n / total) * 100) if total > 0 else 0

# Narrative banner — must be visible before any chart
st.markdown(
    f"""
    <div style="background-color:#1a2640; color:#ffffff; border-radius:10px;
                padding:18px 24px; margin-bottom:20px; font-size:15px;
                line-height:1.7;">
    📊 <strong>Key finding:</strong> In Q1 2024,
    <strong>{non_cyber_pct}%</strong> of the <strong>{total:,}</strong>
    reported incidents were caused by <strong>human error</strong> —
    not sophisticated cyber-attacks. Yet <strong>{non_compliant_pct}%</strong>
    of organisations failed to report breaches within GDPR's mandatory
    72-hour deadline, leaving data subjects vulnerable and regulators unaware.
    </div>
    """,
    unsafe_allow_html=True,
)

# KPI cards
compliant_pct = round(compliant_n / total * 100) if total > 0 else 0
top_type = filtered["Incident Type"].value_counts().idxmax()
top_type_display = top_type if len(top_type) < 30 else top_type[:27] + "..."

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total incidents", f"{total:,}")
col2.metric("Human error (non-cyber)", f"{non_cyber_pct}%")
col3.metric("GDPR 72hr compliant", f"{compliant_pct}%")
col4.metric("Top breach type", top_type_display)
```

**Test:** Change a filter. Do all four KPI numbers update? Does the narrative
percentage update? If the numbers stay fixed, check that you are using
`filtered` not `df_incidents` in the calculations.

---

### Section E — INTERPRET (trend and top types)

```python
st.markdown("---")

# Chart 1 — full width
st.caption(
    "Monthly volume split by incident category — "
    "showing whether the problem grew, stabilised, or declined across Q1."
)
st.plotly_chart(chart_monthly_trend(filtered), use_container_width=True)

st.markdown("---")

# Charts 2 and 3 — side by side
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Top incident types")
    st.caption(
        "Ranked by frequency — reveals that misdirected emails, "
        "not ransomware, dominate UK data security incidents."
    )
    st.plotly_chart(chart_incident_types(filtered), use_container_width=True)

with col_right:
    st.markdown("#### GDPR 72-hour compliance by sector")
    st.caption(
        "Reporting time bands per sector — "
        "red indicates breach of GDPR's 72-hour reporting obligation."
    )
    st.plotly_chart(chart_gdpr_compliance(filtered), use_container_width=True)
```

---

### Section F — COMPREHEND (full picture)

```python
st.markdown("---")

# Chart 4 — full width
st.markdown("#### Sectoral vulnerability — cyber vs human error")
st.caption(
    "Which sectors face the most incidents, "
    "and what proportion stems from human error vs cyber attack?"
)
st.plotly_chart(chart_sector_vulnerability(filtered), use_container_width=True)

st.markdown("---")

# Charts 5 and 6 — side by side
col5, col6 = st.columns(2)

with col5:
    st.markdown("#### Data types exposed")
    st.caption(
        "What categories of personal data are most frequently "
        "compromised in a breach? (counts all data types per incident)"
    )
    st.plotly_chart(chart_data_types(filtered_raw), use_container_width=True)

with col6:
    st.markdown("#### Regulatory decisions")
    st.caption(
        "What regulatory action did the ICO take "
        "following each reported incident?"
    )
    st.plotly_chart(
        chart_regulatory_decisions(filtered), use_container_width=True
    )

# Raw data expander
st.markdown("---")
with st.expander("📋 View filtered incident records"):
    display_cols = [
        "BI Reference", "Sector", "Incident Category", "Incident Type",
        "No. Data Subjects Affected", "Time Taken to Report",
        "GDPR Compliant", "Decision Taken",
    ]
    # Only show columns that exist in the filtered dataframe
    display_cols = [c for c in display_cols if c in filtered.columns]
    st.dataframe(filtered[display_cols], use_container_width=True, height=300)
    st.caption(
        f"Each row = one unique breach incident. "
        f"{len(filtered):,} incidents shown."
    )

# Footer
st.markdown(
    """
    <div style="text-align:center; color:#888; font-size:12px;
                margin-top:40px; padding-top:20px;
                border-top:1px solid #e0e0e0;">
    Data source: ICO (2026) Data Security Incident Trends |
    Built with Python · Pandas · Plotly · Streamlit |
    CETM25 Assignment 2 — University of Sunderland
    </div>
    """,
    unsafe_allow_html=True,
)
```

---

### STOP AND CHECK — Phase 4

```
[ ] Does the narrative banner appear above all charts?
[ ] Do all 4 KPI cards update when you change a filter?
[ ] Do all 6 charts update simultaneously on filter change?
[ ] What happens when you deselect all sectors?
    Does the guard clause message appear cleanly?
    Answer: _______________

[ ] Does Chart 5 still show correct data when filters are applied?
    (It uses filtered_raw, not filtered — check the row count in the expander)

[ ] How long does a filter change take to update all charts?
    Under 3 seconds? Over?
    Answer: _______________

[ ] Is the key finding visible without scrolling on your screen?
    Answer: Yes / No

Write down any error that appeared and how you resolved it:
Error: _______________
Resolution: _______________
```

---

## Phase 5 — Final checks before submission

Run through this checklist on a completely fresh terminal — close everything
and start again from scratch to simulate what a new user would experience.

```bash
# Close terminal, open a new one
cd ico_dashboard
source venv/bin/activate
streamlit run app.py
```

```
[ ] App runs with no errors on fresh terminal?

[ ] Non-functional requirements met:
    [ ] All chart axes start at zero
    [ ] No two colours are distinguishable by hue alone
        (palette already satisfies this)
    [ ] All axis labels in plain English — no column abbreviations
    [ ] Dashboard loads and is readable within 5 minutes
        without any prior explanation
    [ ] Filter response is under 3 seconds

[ ] Data accuracy:
    [ ] Total incident count matches your Phase 2 verification number
    [ ] GDPR compliance % matches your Phase 2 calculation
    [ ] Top incident type matches your Phase 2 verification

[ ] Storytelling:
    [ ] Central narrative is visible without scrolling
    [ ] Chart 2 makes the email vs ransomware finding obvious
        without any annotation
    [ ] A non-technical person can read the key finding
        without needing to understand the charts

[ ] Submission:
    [ ] Zip the folder: zip -r ico_dashboard.zip ico_dashboard/
    [ ] README.md includes setup instructions
    [ ] requirements.txt is present and correct
    [ ] ico_raw.csv is NOT included in the zip
        (it is too large and is publicly available — reference the URL instead)
```

---

## What to write in your System Testing section (report Section 1.3)

By the time you reach here, your STOP AND CHECK boxes give you everything
you need. Structure Section 1.3 using these observations:

**Data integrity testing:** Report the three numbers — raw rows, filtered rows,
deduplicated incidents. Explain why deduplication was necessary and what would
have happened without it (inflated counts).

**Accuracy validation:** Report your GDPR compliance rate and compare it to
the ICO's published benchmark. Note any discrepancy and explain it.

**Functional testing:** Report what happened when filters combined to return
zero results, and how the guard clause handled it.

**Performance testing:** Report the actual filter response time you observed
and confirm whether it met the 3-second non-functional requirement.

**Boundary testing:** Report what unexpected values or edge cases you
encountered in the real dataset that the sample data did not reveal.

---

## Reference for your report

All observations from this guide map to these referenced concepts:

| Observation | Academic reference |
|---|---|
| Deduplication logic and preprocessing pipeline | Kirk (2024) — trustworthiness as the foundation of visualisation design |
| Iterative chart-by-chart development | Rahy and Bass (2022) — agile, incremental software development |
| GDPR compliance rate cross-validation | ICO (2026) — published Q1 2024 benchmark figures |
| Guard clause for empty filter results | Rahy and Bass (2022) — non-functional requirement validation |
| 5-minute operability test | Lennerholt, Van Laere and Söderström (2021) — SSBI ease of use |
| Counter-intuitive finding in Chart 2 | Shao et al. (2024) — design to reveal unexpected insights |
| Perceive → interpret → comprehend layout | Kirk (2024) — three-phase audience journey |
