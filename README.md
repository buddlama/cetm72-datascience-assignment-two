# UK Data Security Incidents Dashboard — Q1 2024

A multi-page Streamlit dashboard built on ICO Data Security Incident Trends
data, developed for CETM25 (Data Visualisation) Assignment 2, University of
Sunderland.

## What this is

An interactive prototype exploring personal data breach reports made to the
UK Information Commissioner's Office (ICO) during Q1 2024 (January–March).
Built for two audiences: junior government officials needing a self-service
overview, and data journalists seeking evidence-based reporting material.

## Project structure

```
dashboard_project/
├── app.py                          Home page (entry point)
├── utils/
│   ├── data.py                     load_data(), apply_filters(), shared constants
│   └── charts.py                   All chart-building functions
├── pages/
│   ├── 1_Narrative.py              Written summary with inline stats
│   ├── 2_Incident_Types.py         Incident type breakdown (bar/funnel toggle)
│   ├── 3_Sectoral_Vulnerability.py Sector breakdown (chart/table toggle, scale chart)
│   └── 4_GDPR_Compliance.py        Compliance by sector/category/decision/scale
├── tests/
│   ├── fixture_data.csv            Small synthetic dataset used by tests
│   ├── test_data_integrity.py      Category 1: data correctness tests
│   ├── test_functional_requirements.py  Category 2: requirements tests
│   └── requirements_traceability.md     Manual verification log
└── PROJECT_SPECIFICATION.md        Assignment 1 scope vs. what was built
```

## Setup

Requires Python 3.9+.

```bash
pip install streamlit pandas plotly pytest
```

## Running the dashboard

1. Place your ICO dataset CSV in the project root, named `ico-dataset.csv`
   (or update `DATA_PATH` in `utils/data.py` to match your filename).
2. From the project root:

```bash
streamlit run app.py
```

3. Streamlit will open a browser tab. Use the sidebar to navigate between
   pages — Home, Narrative, Incident Types, Sectoral Vulnerability, GDPR
   Compliance.

## Running the tests

```bash
pytest tests/ -v
```

Tests run against a small synthetic fixture (`tests/fixture_data.csv`), not
the real dataset — this keeps tests fast, deterministic, and independent of
whatever data file happens to be present locally.

## Data expectations

The dashboard expects a CSV with these exact column headers (matching the
ICO's published format):

```
BI Reference, Year, Quarter, Data Subject Type, Data Type, Decision Taken,
Incident Category, Incident Type, No. Data Subjects Affected, Sector,
Time Taken to Report
```

The dashboard automatically filters to Q1 2024 regardless of the date range
in the source file, so a multi-year dataset can be used directly.

## Further documentation

- **`PROJECT_SPECIFICATION.md`** — what Assignment 1 proposed, what was
  actually built, and why each deviation happened. Source material for the
  Assignment 2 write-up.
- **`tests/requirements_traceability.md`** — which requirements were
  verified automatically vs. manually, and what remains unverified.
