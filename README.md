# UK Data Security Incidents Dashboard — Q1 2024

A multi-page Streamlit dashboard built on ICO Data Security Incident Trends
data, developed for CETM72 (Data Science) Assignment 2, University of
Sunderland.

## What this is

An interactive prototype exploring personal data breach reports made to the
UK Information Commissioner's Office (ICO) during Q1 2024 (January–March).
Built for two audiences: junior government officials needing a self-service
overview, and data journalists seeking evidence-based reporting material.

## Project structure

```
cetm72-datascience-assignment-two/
├── app.py                          Home page (entry point)
├── requirements.txt                Pinned Python dependencies
├── utils/
│   ├── data.py                     load_data(), apply_filters(), shared constants
│   ├── charts.py                   All chart-building functions
│   └── colours.py                  Central colour palette (WCAG-compliant constants)
├── pages/
│   ├── 1_Narrative.py              Written summary with inline stats
│   ├── 2_Incident_Types.py         Incident type bar chart + breach scale line chart
│   ├── 3_Sectoral_Vulnerability.py Sector stacked bar chart + frequency vs impact bubble chart
│   └── 4_GDPR_Compliance.py        GDPR compliance by sector, category, and regulatory decision
├── tests/
│   ├── fixture_data.csv                 Small synthetic dataset used by tests
│   ├── test_data_integrity.py           Category 1: data correctness tests
│   ├── test_functional_requirements.py  Category 2: requirements traceability tests
│   ├── test_accessibility.py            Category 3: WCAG colour contrast tests
│   └── requirements_traceability.md     Manual verification log
├── CHARTS_README.md                Chart-by-chart documentation (what, why, audience)
└── PROJECT_SPECIFICATION.md        Assignment 1 scope vs. what was built
```

## Setup

Requires Python 3.9+.

> **Mac users:** create a virtual environment first to avoid conflicts with the system Python:
> ```bash
> python3 -m venv venv && source venv/bin/activate
> ```

```bash
pip install -r requirements.txt
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

The test suite has three categories:

| File | What it covers |
|---|---|
| `test_data_integrity.py` | Column presence, type correctness, value constraints |
| `test_functional_requirements.py` | Filter logic, chart-data linkage, GDPR 72-hour rule, performance |
| `test_accessibility.py` | WCAG 1.4.11 contrast ratios (≥ 3:1 on white) for every palette colour |

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

## Deploying to Streamlit Cloud

Anyone can host this dashboard publicly for free using their own GitHub account
and [Streamlit Community Cloud](https://streamlit.io/cloud). No server or
Docker knowledge required.

### Prerequisites

- A [GitHub](https://github.com) account
- A [Streamlit Community Cloud](https://share.streamlit.io) account (free, sign
  in with GitHub)

### Steps

1. **Fork or push this repository to your own GitHub account.**
   The repo must be public (or you must be on a Streamlit Cloud plan that
   supports private repos).

2. **Make sure `ico-dataset.csv` is committed to the repository.**
   Streamlit Cloud clones your repo at deploy time — if the data file is listed
   in `.gitignore` or was never committed, the app will fail to start.
   Verify it is tracked:
   ```bash
   git ls-files ico-dataset.csv
   ```
   If it prints nothing, add and commit it:
   ```bash
   git add ico-dataset.csv
   git commit -m "add dataset"
   git push
   ```

3. **Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.**

4. **Click "Create app" and fill in:**

   | Field | Value |
   |---|---|
   | Repository | `your-github-username/your-repo-name` |
   | Branch | `main` (or whichever branch has your latest code) |
   | Main file path | `app.py` |

5. **Click "Deploy".**
   Streamlit Cloud reads `requirements.txt` automatically and installs all
   dependencies. The build takes 1–3 minutes.

6. **Your app is live** at a URL like:
   `https://your-username-your-repo-name-app-xxxxx.streamlit.app`

### Notes

- `requirements.txt` is already included in this repo — no changes needed.
- The dataset file is 32 MB, which is well within GitHub's 100 MB per-file
  limit. If you ever use a larger dataset, host it externally (e.g. Google
  Sheets or a public URL) and update `DATA_PATH` in `utils/data.py`.
- Any push to the deployed branch automatically triggers a re-deploy.

---

## Further documentation

- **`CHARTS_README.md`** — chart-by-chart documentation: what each chart
  shows, what the audience learns from it, and why that chart type was chosen.
- **`PROJECT_SPECIFICATION.md`** — what Assignment 1 proposed, what was
  actually built, and why each deviation happened. Source material for the
  Assignment 2 write-up.
- **`tests/requirements_traceability.md`** — which requirements were
  verified automatically vs. manually, and what remains unverified.
