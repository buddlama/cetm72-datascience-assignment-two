# ICO Data Security Incident Trends Dashboard — Q1 2024

**CETM25 Assignment 2 Prototype | Buddha Lama | University of Sunderland**

---

## Overview

An interactive Streamlit dashboard visualising UK data security incidents reported to the Information Commissioner's Office (ICO) in Q1 2024 (January–March 2024).

**Central narrative:** In Q1 2024, the most serious threat to UK data security was not sophisticated cyber-attacks, but human error — yet a significant proportion of organisations failed to report breaches within GDPR's mandatory 72-hour deadline.

---

## Requirements

- Python 3.9+
- pip

---

## Installation

### 1. Clone or unzip the project folder

```bash
cd ico_dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Dashboard

```bash
streamlit run app.py
```

Then open your browser at: **http://localhost:8501**

> No installation of data science tools or coding knowledge is required beyond the above steps.

---

## Using the Dashboard

Once open in your browser:

1. **Use the sidebar filters** (left panel) to narrow by Sector, Incident Category, or Time Taken to Report
2. **Charts update automatically** in response to your filter selections
3. **Scroll down** to explore all five visualisation panels
4. **Expand "View filtered incident data"** at the bottom to inspect the underlying records

---

## Data Source

ICO (2026) _Data Security Incident Trends Dataset_. Information Commissioner's Office.
Available at: https://ico.org.uk/action-weve-taken/complaints-and-concerns-data-sets/data-security-incident-trends/

**To use the real ICO dataset:**

1. Download the full dataset from the ICO website (Excel/CSV format)
2. Filter rows to `Year = 2024` and `Quarter = Qtr 1`
3. Save as `ico_q1_2024_sample.csv` in this folder (replacing the sample file)
4. Restart the app — all charts will update automatically

The sample dataset (`ico_q1_2024_sample.csv`) included here replicates the exact column structure, value formats, and Q1 2024 proportions reported by the ICO, for demonstration purposes.

---

## Visualisations Included

| Chart                     | Type           | Purpose                                          |
| ------------------------- | -------------- | ------------------------------------------------ |
| Incident trend            | Line chart     | Monthly volume Jan–Mar, split by cyber/non-cyber |
| Top incident types        | Horizontal bar | Most frequent breach types ranked                |
| GDPR compliance by sector | Stacked bar    | Reporting time bands per sector                  |
| Sectoral vulnerability    | Stacked bar    | Cyber vs human error per industry                |
| Data types exposed        | Donut chart    | Categories of personal data compromised          |
| Regulatory decisions      | Bar chart      | ICO outcomes per incident                        |

---

## Project Structure

```
ico_dashboard/
├── app.py                    # Main Streamlit application
├── data_generator.py         # Sample data generation script
├── ico_q1_2024_sample.csv    # Sample dataset (Q1 2024 format)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## References

- ICO (2026) Data Security Incident Trends Dataset. Available at: https://ico.org.uk/action-weve-taken/complaints-and-concerns-data-sets/data-security-incident-trends/
- Kirk, A. (2024) _Data Visualisation: A Handbook for Data Driven Design_. Third edition. London: SAGE Publications.
- Shao, H. et al. (2024) 'Data Storytelling in Data Visualisation'. ACM.
- Franconeri, S.L. et al. (2021) 'The Science of Visual Data Communication'. _Psychological Science in the Public Interest_, 22(3).
