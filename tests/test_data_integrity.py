# tests/test_data_integrity.py
#
# Category 1: Data Integrity and Accuracy Testing
#
# Rationale (per project decision log D-22): these tests address the risk
# that a visually polished dashboard can still mislead its audience if the
# underlying data pipeline is wrong — the "garbage in, garbage out" problem
# (Lisnic et al., 2023; Midway, 2020). Each test below verifies one specific
# point in the data pipeline (load -> filter -> aggregate) is correct,
# independent of how the resulting chart looks.
#
# Run with: pytest tests/test_data_integrity.py -v

import sys
import os
import pytest
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.data import load_data, apply_filters, SUBJECTS_AFFECTED_ORDER
from utils.charts import (
    gdpr_compliance_by_sector,
    gdpr_compliance_by_category,
    gdpr_compliance_by_decision,
    sector_category_counts,
)

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixture_data.csv")


@pytest.fixture
def loaded_data():
    """Loads the small synthetic fixture once per test that needs it."""
    df_incidents, df_rows = load_data(FIXTURE_PATH)
    return df_incidents, df_rows


# ─────────────────────────────────────────────────────────────────────────
# 1. Q1 2024 date filter correctness
# ─────────────────────────────────────────────────────────────────────────

def test_only_q1_2024_present(loaded_data):
    """
    Fixture includes BI9007 (Q4 2023) and BI9008 (Q2 2024) deliberately.
    Both must be excluded after load_data() filters to Q1 2024 only.
    """
    df_incidents, df_rows = loaded_data

    assert (df_incidents["year"] == 2024).all()
    assert (df_incidents["quarter"] == "Qtr 1").all()
    assert "BI9007" not in df_incidents["bi_ref"].values
    assert "BI9008" not in df_incidents["bi_ref"].values


def test_q1_2024_incidents_retained(loaded_data):
    """The six genuine Q1 2024 incidents (BI9001-BI9006) must all survive filtering."""
    df_incidents, df_rows = loaded_data
    expected_ids = {"BI9001", "BI9002", "BI9003", "BI9004", "BI9005", "BI9006"}
    assert set(df_incidents["bi_ref"].values) == expected_ids


# ─────────────────────────────────────────────────────────────────────────
# 2. Deduplication correctness (D-01)
# ─────────────────────────────────────────────────────────────────────────

def test_df_incidents_has_no_duplicate_bi_refs(loaded_data):
    df_incidents, df_rows = loaded_data
    assert df_incidents["bi_ref"].is_unique


def test_df_incidents_one_row_per_bi_ref(loaded_data):
    """BI9001 has 3 rows in the raw data (3 data types) -> must collapse to 1 in df_incidents."""
    df_incidents, df_rows = loaded_data
    bi9001_rows = df_incidents[df_incidents["bi_ref"] == "BI9001"]
    assert len(bi9001_rows) == 1


def test_df_rows_preserves_all_data_type_rows(loaded_data):
    """
    D-01: df_rows must NOT be deduplicated — BI9001's 3 data type rows
    must all still be present, unlike df_incidents.
    """
    df_incidents, df_rows = loaded_data
    bi9001_rows = df_rows[df_rows["bi_ref"] == "BI9001"]
    assert len(bi9001_rows) == 3
    assert set(bi9001_rows["data_type"].values) == {
        "Health data", "Location data", "Identification data"
    }


def test_df_rows_row_count_gte_df_incidents(loaded_data):
    """df_rows can never have fewer rows than df_incidents — structural invariant."""
    df_incidents, df_rows = loaded_data
    assert len(df_rows) >= len(df_incidents)


# ─────────────────────────────────────────────────────────────────────────
# 3. GDPR compliance flag correctness (D-02)
# ─────────────────────────────────────────────────────────────────────────

def test_gdpr_compliant_bands_flagged_true(loaded_data):
    df_incidents, df_rows = loaded_data
    compliant_bands = ["Less than 24 hours", "24 hours to 72 hours"]
    compliant_rows = df_incidents[df_incidents["time_to_report"].isin(compliant_bands)]
    assert compliant_rows["gdpr_compliant"].all()


def test_gdpr_noncompliant_bands_flagged_false(loaded_data):
    df_incidents, df_rows = loaded_data
    noncompliant_bands = ["72 hours to 1 week", "More than 1 week"]
    noncompliant_rows = df_incidents[df_incidents["time_to_report"].isin(noncompliant_bands)]
    assert not noncompliant_rows["gdpr_compliant"].any()


def test_gdpr_flag_is_boolean_dtype(loaded_data):
    df_incidents, df_rows = loaded_data
    assert df_incidents["gdpr_compliant"].dtype == bool


# ─────────────────────────────────────────────────────────────────────────
# 4. Whitespace stripping correctness
# ─────────────────────────────────────────────────────────────────────────

def test_no_leading_trailing_whitespace_in_text_columns(loaded_data):
    df_incidents, df_rows = loaded_data
    str_cols = df_incidents.select_dtypes(include=["string", "object"]).columns
    for col in str_cols:
        values = df_incidents[col].dropna()
        for v in values:
            assert v == v.strip(), f"Untrimmed whitespace found in column '{col}': '{v}'"


# ─────────────────────────────────────────────────────────────────────────
# 5. Filter correctness (apply_filters)
# ─────────────────────────────────────────────────────────────────────────

def test_filter_never_increases_row_count(loaded_data):
    df_incidents, df_rows = loaded_data
    filtered = apply_filters(df_incidents, sectors=["Health"])
    assert len(filtered) <= len(df_incidents)


def test_filter_by_sector_returns_only_that_sector(loaded_data):
    df_incidents, df_rows = loaded_data
    filtered = apply_filters(df_incidents, sectors=["Health"])
    assert (filtered["sector"] == "Health").all()


def test_filter_with_no_selection_returns_everything(loaded_data):
    """Empty/None filter values should mean 'no filter applied', not 'show nothing'."""
    df_incidents, df_rows = loaded_data
    filtered = apply_filters(df_incidents)
    assert len(filtered) == len(df_incidents)


def test_filter_combination_is_and_logic(loaded_data):
    """Sector + category together should narrow further than either alone."""
    df_incidents, df_rows = loaded_data
    sector_only = apply_filters(df_incidents, sectors=["Health"])
    sector_and_category = apply_filters(df_incidents, sectors=["Health"], categories=["Cyber"])
    assert len(sector_and_category) <= len(sector_only)


def test_filter_multiselect_is_or_logic_within_field(loaded_data):
    """Selecting two sectors should return incidents from EITHER, not neither/both required."""
    df_incidents, df_rows = loaded_data
    filtered = apply_filters(df_incidents, sectors=["Health", "Legal"])
    assert set(filtered["sector"].unique()).issubset({"Health", "Legal"})
    assert len(filtered) == len(
        df_incidents[df_incidents["sector"].isin(["Health", "Legal"])]
    )


def test_filter_nonexistent_value_returns_empty(loaded_data):
    df_incidents, df_rows = loaded_data
    filtered = apply_filters(df_incidents, sectors=["NonexistentSector"])
    assert len(filtered) == 0


def test_data_type_not_a_filter_parameter(loaded_data):
    """
    D-01 scope decision: data_type is deliberately NOT a filter parameter
    on apply_filters(), since df_incidents only retains one data_type value
    per incident. This test documents that omission is intentional.
    """
    import inspect
    sig = inspect.signature(apply_filters)
    assert "data_type" not in sig.parameters


# ─────────────────────────────────────────────────────────────────────────
# 6. Aggregation totals reconcile with filtered row count
# ─────────────────────────────────────────────────────────────────────────

def test_sector_category_counts_total_matches_filtered_count(loaded_data):
    df_incidents, df_rows = loaded_data
    counts = sector_category_counts(df_incidents)
    assert counts["count"].sum() == len(df_incidents)


def test_gdpr_by_sector_totals_match_filtered_count(loaded_data):
    df_incidents, df_rows = loaded_data
    summary = gdpr_compliance_by_sector(df_incidents)
    assert summary["total"].sum() == len(df_incidents)


def test_gdpr_by_category_totals_match_filtered_count(loaded_data):
    df_incidents, df_rows = loaded_data
    summary = gdpr_compliance_by_category(df_incidents)
    assert summary["total"].sum() == len(df_incidents)


def test_gdpr_by_decision_totals_match_filtered_count(loaded_data):
    df_incidents, df_rows = loaded_data
    summary = gdpr_compliance_by_decision(df_incidents)
    assert summary["total"].sum() == len(df_incidents)


def test_compliant_count_never_exceeds_total(loaded_data):
    """Sanity bound: compliant incidents per group can't exceed that group's total."""
    df_incidents, df_rows = loaded_data
    summary = gdpr_compliance_by_sector(df_incidents)
    assert (summary["compliant"] <= summary["total"]).all()


def test_compliance_percentage_within_valid_range(loaded_data):
    df_incidents, df_rows = loaded_data
    summary = gdpr_compliance_by_sector(df_incidents)
    assert (summary["compliance_pct"] >= 0).all()
    assert (summary["compliance_pct"] <= 100).all()


# ─────────────────────────────────────────────────────────────────────────
# 7. Band ordering integrity (D-15)
# ─────────────────────────────────────────────────────────────────────────

def test_subjects_affected_order_constant_is_complete(loaded_data):
    """
    Every value of subjects_affected actually present in the data must be
    covered by SUBJECTS_AFFECTED_ORDER, or charts using it would silently
    drop or misplace bands.
    """
    df_incidents, df_rows = loaded_data
    actual_values = set(df_incidents["subjects_affected"].unique())
    assert actual_values.issubset(set(SUBJECTS_AFFECTED_ORDER))


def test_subjects_affected_order_is_logically_sequenced():
    """Guards against accidental reordering of the band list itself."""
    assert SUBJECTS_AFFECTED_ORDER == [
        "1 to 9", "10 to 99", "100 to 1k", "1k to 10k", "10k to 100k"
    ]
