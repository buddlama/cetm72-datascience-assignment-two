"""
Generates a realistic sample of the ICO Data Security Incident Trends dataset
filtered to Q1 2024 (January–March 2024), matching the ICO's actual column schema.
Replace this file with the real ICO CSV when available.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

SECTORS = {
    "Health": 0.18,
    "Finance, insurance and credit": 0.13,
    "Education and childcare": 0.12,
    "General business": 0.10,
    "Local government": 0.09,
    "Legal": 0.08,
    "Retail and manufacture": 0.07,
    "Charitable and voluntary": 0.06,
    "Transport and leisure": 0.05,
    "Central government": 0.04,
    "Land or property services": 0.04,
    "Other": 0.04,
}

INCIDENT_TYPES = {
    "Non-cyber": {
        "Emailed to wrong recipient": 0.16,
        "Data posted or faxed to wrong recipient": 0.10,
        "Loss or theft of paperwork": 0.09,
        "Failure to redact": 0.08,
        "Verbal disclosure": 0.07,
        "Loss or theft of device": 0.06,
        "Uploaded to website in error": 0.05,
        "Other non-cyber": 0.11,
    },
    "Cyber": {
        "Phishing": 0.08,
        "Ransomware": 0.05,
        "Unauthorised access": 0.05,
        "Malware (not ransomware)": 0.04,
        "Brute force attack": 0.03,
        "Other cyber": 0.03,
    },
}

INCIDENT_CATEGORIES = ["Non-cyber", "Cyber"]

REGULATORY_DECISIONS = {
    "No further action": 0.55,
    "Advice given": 0.25,
    "Reprimand issued": 0.10,
    "Under investigation": 0.07,
    "Referred to enforcement": 0.03,
}


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def generate_dataset(n=2970):
    records = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)

    sector_list = list(SECTORS.keys())
    sector_weights = list(SECTORS.values())

    for i in range(n):
        # Sector
        sector = random.choices(sector_list, weights=sector_weights)[0]

        # Incident category (non-cyber ~73%, cyber ~27%)
        category = random.choices(["Non-cyber", "Cyber"], weights=[0.73, 0.27])[0]

        # Incident type within category
        type_pool = INCIDENT_TYPES[category]
        type_keys = list(type_pool.keys())
        type_weights = list(type_pool.values())
        incident_type = random.choices(type_keys, weights=type_weights)[0]

        # Notification date
        notification_date = random_date(start_date, end_date)

        # Hours to report (GDPR requires 72h; ~62% comply)
        compliant = random.random() < 0.62
        if compliant:
            hours_to_report = round(random.uniform(1, 72), 1)
        else:
            hours_to_report = round(random.uniform(73, 720), 1)

        gdpr_compliant = "Yes" if hours_to_report <= 72 else "No"

        # Data subjects affected
        subjects = int(np.random.lognormal(mean=3.5, sigma=1.8))
        subjects = max(1, min(subjects, 500000))

        # Regulatory decision
        decision = random.choices(
            list(REGULATORY_DECISIONS.keys()),
            weights=list(REGULATORY_DECISIONS.values()),
        )[0]

        # BI reference (unique ID)
        bi_ref = f"BI-2024-{str(i+1).zfill(5)}"

        records.append({
            "BI Reference": bi_ref,
            "Notification Date": notification_date.strftime("%Y-%m-%d"),
            "Month": notification_date.strftime("%B"),
            "Quarter": "Q1 2024",
            "Sector": sector,
            "Incident Category": category,
            "Incident Type": incident_type,
            "Data Subjects Affected": subjects,
            "Hours to Report": hours_to_report,
            "GDPR 72hr Compliant": gdpr_compliant,
            "Regulatory Decision": decision,
        })

    df = pd.DataFrame(records)
    # Ensure month order
    month_order = {"January": 1, "February": 2, "March": 3}
    df["Month_Num"] = df["Month"].map(month_order)
    df = df.sort_values("Month_Num").drop(columns="Month_Num")
    return df


if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv("ico_q1_2024_sample.csv", index=False)
    print(f"Generated {len(df)} records")
    print(df.dtypes)
    print(df.head(3))
