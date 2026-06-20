# Project Specification — Assignment 1 Plan vs. Assignment 2 Implementation

CETM25 Data Visualisation | Buddha Lama | University of Sunderland

This document tracks the relationship between the design plan proposed in
Assignment 1 and what was actually implemented during Assignment 2
prototype development. Differences between plan and implementation are
documented with rationale, not hidden — this reflects the iterative,
evidence-based nature of real visualisation design work, consistent with
Kirk's (2024) and Shao et al.'s (2024) emphasis on letting the data inform
the design rather than forcing data to fit a pre-set plan.

---

## 1. Original Scope (Assignment 1)

**Dataset:** ICO Data Security Incident Trends, filtered to Q1 2024
(January–March), deduplicated by BI Reference.

**Audiences:** Junior government officials (primary), data journalists
(secondary).

**Planned insights (four):**
1. Incident trend — line chart
2. Incident type composition — horizontal bar chart
3. Sectoral vulnerability — stacked bar chart
4. GDPR compliance rates — colour-blind safe bar chart

**Planned interactivity:** Filtering by sector, incident type, incident
category, time taken to report.

**Planned architecture:** Python, Pandas (preprocessing), Plotly
(visualisation), Streamlit (deployment).

---

## 2. What Was Actually Built

### 2.1 Data Architecture — Two-Table Approach

The original plan described removing duplicate BI Reference entries as a
single preprocessing step. On inspection of the real data, this was found
to be incomplete: one incident can expose multiple data types, producing
multiple rows per incident. Blind deduplication would silently discard
valid records.

**Implemented instead:** `load_data()` returns two DataFrames —
`df_incidents` (one row per incident, used for all incident-count charts)
and `df_rows` (full dataset, preserved for data-type-level analysis).
See Decision Log entries D-01.

### 2.2 Page Structure

The original plan implied a single-page dashboard. During development this
was restructured into a multi-page app (Home, Narrative, and one page per
chart topic), modelled on the official ICO Power BI dashboard's
information architecture. Each page has filters scoped to its own
question, rather than one global filter bar affecting all charts
regardless of relevance. See D-13.

| Page | Purpose |
|---|---|
| Home (`app.py`) | Orientation — purpose statement, content map |
| Narrative | Written summary of Q1 2024 findings, in prose, with inline stats |
| Incident Types | How breaches occurred (bar chart / funnel chart toggle) |
| Sectoral Vulnerability | Which sectors are most affected (chart / table toggle), plus breach scale by sector |
| GDPR Compliance | Compliance rate by sector, category, regulatory decision, and breach scale |

### 2.3 Charts — Planned vs. Delivered

| Planned Insight | Status | Notes |
|---|---|---|
| Incident type composition (bar) | **Delivered** | Plus funnel chart alternative view |
| Sectoral vulnerability (stacked bar) | **Delivered** | Plus breach-scale-by-sector chart |
| GDPR compliance (bar) | **Delivered** | Plus dot-plot alternative, plus three additional compliance breakdowns (see 2.4) |
| Incident trend (line chart) | **Not delivered** | See 2.5 — scope limitation, documented rather than forced |

### 2.4 Additional Charts Beyond Original Plan

During Assignment 2 development, several additional insights were
identified and built, beyond the original four. Each was evaluated for
feasibility and narrative fit before being built (see Decision Log D-16
onward) rather than added speculatively:

- GDPR compliance by Incident Category (Cyber vs Non-Cyber) — tests
  whether human-error-dominant incidents are also slower to report.
  **Finding:** the opposite was true; Non-Cyber incidents were marginally
  *more* compliant. (D-17)
- GDPR compliance by Decision Taken — tests whether incidents triggering
  formal ICO action were reported more slowly. **Finding:** only a 7-point
  spread across decision types; no dramatic pattern. (D-19)
- GDPR compliance by breach scale (subjects affected) — tests whether
  larger breaches are reported more slowly. **Finding:** no clean
  monotonic relationship; largest band has smallest sample size, surfaced
  directly in the chart rather than smoothed over. (D-21)
- Breach scale by sector — distinct from incident *count* by sector,
  shows which sectors have the largest-scale breaches by people affected.
  (D-20)
- Summary metric row (filtered incident count, non-cyber %, compliant %)
  added to every chart page, mirroring the official ICO dashboard's
  stat-box pattern. (D-16)

One additional idea (subjects affected by incident type, intended to show
"human error" population impact) was investigated and discarded after the
underlying hypothesis was disconfirmed by the data (D-14, D-18). A further
idea (sector × incident type cross-tabulation) was considered and
deliberately not pursued, to avoid diluting page-level clarity after
several additions had already been made (see Decision Log, scope
checkpoint discussion).

### 2.5 Incident Trend Chart — Scope Limitation

The planned line chart could not be meaningfully built within the
project's Q1-2024-only scope: a single quarter provides no time axis to
trend across. Three alternatives were considered (reinterpreting the axis
as reporting-delay bands; scoping only this chart to the full 2019–2025
date range; substituting a different chart type) but each either departs
from the original chart specification or breaks the date-scope consistency
applied to the rest of the dashboard. The decision was made not to
implement this chart, leaving three core insights plus several
compliance-focused extensions rather than the originally planned four. See
D-11.

---

## 3. Design Principles Applied

Drawing on the module's Question 1 (Good Visualisation Design) and
Question 2 (Key Risks) literature:

- **Preattentive accent colouring** (Knaflic, 2015) — charts use grey for
  non-focal categories and a single colour-blind safe accent (#D55E00,
  Wong 2011 palette) to draw attention to the headline finding, rather
  than using equal-weight colour across all categories.
- **Action titles** (Knaflic, 2015) — chart titles state the finding
  itself (e.g. "Human Error, Not Cyber-Attack, Is the Leading Cause of
  Data Breaches") rather than merely labelling the topic.
- **Minimalism** (Knaflic, 2015; Wilke, 2019) — gridlines removed where
  not load-bearing; data labels placed directly on bars rather than
  requiring a separate legend.
- **Honest representation of uncertain or weak findings** (Correll, 2019)
  — where a relationship in the data was weak or non-monotonic (e.g. GDPR
  compliance by decision taken, by breach scale), charts were deliberately
  built to avoid implying a stronger pattern than the data supports, even
  where a single accent colour might have made the chart look more
  "finished."
- **Sample size transparency** — small-sample sectors and bands are shown
  with their `n=` count directly in the chart, rather than hidden or
  visually equated with large-sample categories, addressing the risk that
  a confident-looking chart built on a small sample misleads its audience
  (Bresciani and Eppler, 2015).

---

## 4. Testing Approach

See `tests/requirements_traceability.md` for the full breakdown. In
summary, testing was split into two categories:

1. **Data Integrity and Accuracy Testing** (Lisnic et al., 2023; Midway,
   2020) — verifies the data pipeline itself is correct (deduplication,
   filtering, aggregation, the GDPR compliance flag), independent of how
   any chart looks. 25 automated tests in `tests/test_data_integrity.py`.
2. **Functional and Requirements Testing** (Rahy and Bass, 2022; Kirk,
   2024) — verifies the product against the specific functional and
   non-functional requirements stated in Assignment 1. 13 automated tests
   in `tests/test_functional_requirements.py`, supplemented by a manual
   traceability log for requirements that cannot be unit-tested (e.g.
   five-minute non-technical usability).

---

## 5. Full Decision Log Reference

This specification summarises the project's key decisions. The complete,
chronologically ordered decision log (D-01 through D-22+) is maintained
separately and contains the full reasoning, data checks, and rejected
alternatives behind each entry referenced above.
