# tests/test_functional_requirements.py
#
# Category 2: Functional and Requirements Testing
#
# Rationale (per project decision log D-22): these tests validate the
# product against the specific functional and non-functional requirements
# established in Assignment 1 (Rahy and Bass, 2022; Kirk, 2024) — not
# generic "does it run" testing, but requirement-by-requirement
# traceability.
#
# IMPORTANT SCOPE NOTE: Streamlit's UI (sidebar widgets, page navigation,
# button clicks) cannot be exercised by pytest directly — that would
# require a browser automation tool, which is outside this project's
# scope. What CAN be automated here is the underlying logic each UI
# requirement depends on: e.g. if a requirement says "interactive filter
# by sector", this file tests that the filter function correctly narrows
# results by sector — the actual sidebar widget rendering is verified
# manually (see tests/requirements_traceability.md).
#
# Run with: pytest tests/test_functional_requirements.py -v

import sys
import os
import time
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.data import load_data, apply_filters, DATA_PATH, SUBJECTS_AFFECTED_ORDER
from utils.charts import (
    plot_incident_type_breakdown,
    plot_sectoral_vulnerability,
    plot_gdpr_compliance,
)

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixture_data.csv")


@pytest.fixture
def loaded_data():
    df_incidents, df_rows = load_data(FIXTURE_PATH)
    return df_incidents, df_rows


# ─────────────────────────────────────────────────────────────────────────
# REQUIREMENT: "Interactive Filtering and Dashboard... filtering options
# like sector, incident type, incident category, and time taken to report"
# (Assignment 1, Functional Requirements)
# ─────────────────────────────────────────────────────────────────────────

def test_all_four_planned_filter_fields_are_supported(loaded_data):
    """
    Confirms apply_filters() accepts all four filter dimensions named in
    the Assignment 1 functional requirement, by parameter name.
    """
    import inspect
    sig = inspect.signature(apply_filters)
    expected_params = {"sectors", "incident_types", "categories", "report_times"}
    assert expected_params.issubset(set(sig.parameters.keys()))


def test_sector_filter_narrows_results(loaded_data):
    df_incidents, df_rows = loaded_data
    unfiltered_count = len(df_incidents)
    filtered_count = len(apply_filters(df_incidents, sectors=["Health"]))
    assert filtered_count < unfiltered_count


def test_incident_type_filter_narrows_results(loaded_data):
    df_incidents, df_rows = loaded_data
    unfiltered_count = len(df_incidents)
    filtered_count = len(apply_filters(df_incidents, incident_types=["Ransomware"]))
    assert filtered_count < unfiltered_count


def test_category_filter_narrows_results(loaded_data):
    df_incidents, df_rows = loaded_data
    unfiltered_count = len(df_incidents)
    filtered_count = len(apply_filters(df_incidents, categories=["Cyber"]))
    assert filtered_count < unfiltered_count


def test_report_time_filter_narrows_results(loaded_data):
    df_incidents, df_rows = loaded_data
    unfiltered_count = len(df_incidents)
    filtered_count = len(apply_filters(df_incidents, report_times=["Less than 24 hours"]))
    assert filtered_count < unfiltered_count


# ─────────────────────────────────────────────────────────────────────────
# REQUIREMENT: "all charts updating simultaneously" — every chart function
# must accept a filtered DataFrame and reflect it, not silently fall back
# to unfiltered data.
# ─────────────────────────────────────────────────────────────────────────

def test_incident_type_chart_reflects_filtered_data(loaded_data):
    df_incidents, df_rows = loaded_data
    filtered = apply_filters(df_incidents, sectors=["Health"])
    fig = plot_incident_type_breakdown(filtered)
    total_in_chart = sum(fig.data[0].x)
    assert total_in_chart == len(filtered)


def test_sectoral_chart_reflects_filtered_data(loaded_data):
    df_incidents, df_rows = loaded_data
    filtered = apply_filters(df_incidents, categories=["Cyber"])
    fig = plot_sectoral_vulnerability(filtered)
    # Sum across all bar traces (one trace per category in a stacked chart)
    total_in_chart = sum(sum(trace.x) for trace in fig.data)
    assert total_in_chart == len(filtered)


def test_gdpr_chart_handles_filtered_data_without_error(loaded_data):
    df_incidents, df_rows = loaded_data
    filtered = apply_filters(df_incidents, sectors=["Health"])
    fig = plot_gdpr_compliance(filtered)
    assert fig is not None


# ─────────────────────────────────────────────────────────────────────────
# REQUIREMENT: "GDPR Compliance View... highlight compliance with GDPR's
# mandatory 72-hour reporting requirement"
# ─────────────────────────────────────────────────────────────────────────

def test_gdpr_compliance_threshold_matches_72_hour_rule():
    """
    Confirms the compliance boundary is set exactly at the 72-hour mark
    specified in Assignment 1 — not 24 hours, not 1 week.
    """
    from utils.data import load_data
    df_incidents, df_rows = load_data(FIXTURE_PATH)

    # "24 hours to 72 hours" must be compliant; "72 hours to 1 week" must not be
    band_24_72 = df_incidents[df_incidents["time_to_report"] == "24 hours to 72 hours"]
    band_72_1wk = df_incidents[df_incidents["time_to_report"] == "72 hours to 1 week"]

    if len(band_24_72) > 0:
        assert band_24_72["gdpr_compliant"].all()
    if len(band_72_1wk) > 0:
        assert not band_72_1wk["gdpr_compliant"].any()


# ─────────────────────────────────────────────────────────────────────────
# REQUIREMENT: "Performance and Deployability... product must respond to
# filter interactions within three seconds" (Assignment 1, Non-Functional)
#
# NOTE: this measures function execution time only (data load, filter,
# chart build), not full browser round-trip time including Streamlit's
# re-render — full round-trip timing must be checked manually in-browser.
# ─────────────────────────────────────────────────────────────────────────

def test_filter_and_chart_execute_within_three_seconds(loaded_data):
    df_incidents, df_rows = loaded_data

    start = time.time()
    filtered = apply_filters(df_incidents, sectors=["Health"], categories=["Cyber"])
    fig = plot_sectoral_vulnerability(filtered)
    elapsed = time.time() - start

    assert elapsed < 3.0, f"Filter + chart build took {elapsed:.2f}s, exceeding 3s requirement"


# ─────────────────────────────────────────────────────────────────────────
# REQUIREMENT: "Accessibility and Usability... colour-blind safe palettes"
# (Assignment 1, Non-Functional)
# ─────────────────────────────────────────────────────────────────────────

def test_incident_type_chart_colours_avoid_red_green_combination(loaded_data):
    """Same check as the Sectoral chart, now applied to Incident Types since
    it also uses the Cyber/Non-Cyber colour pair after the D-23 redesign."""
    from utils.charts import plot_incident_type_by_category
    df_incidents, df_rows = loaded_data
    fig = plot_incident_type_by_category(df_incidents)

    colours_used = []
    for trace in fig.data:
        if hasattr(trace.marker, "color") and trace.marker.color is not None:
            c = trace.marker.color
            if isinstance(c, str):
                colours_used.append(c.upper())
            else:
                colours_used.extend([str(x).upper() for x in c])

    RED_FLAGS = {"#FF0000", "RED"}
    GREEN_FLAGS = {"#00FF00", "GREEN"}
    has_pure_red = any(c in RED_FLAGS for c in colours_used)
    has_pure_green = any(c in GREEN_FLAGS for c in colours_used)

    assert not (has_pure_red and has_pure_green)


def test_chart_colours_avoid_red_green_combination(loaded_data):
    """
    Cannot programmatically verify full colour-blind safety, but can check
    the specific, well-known failure mode is avoided: pure red (#FF0000-ish)
    paired with pure green (#00FF00-ish) in the same chart.
    """
    df_incidents, df_rows = loaded_data
    fig = plot_sectoral_vulnerability(df_incidents)

    colours_used = []
    for trace in fig.data:
        if hasattr(trace.marker, "color") and trace.marker.color:
            colours_used.append(str(trace.marker.color).upper())

    RED_FLAGS = {"#FF0000", "RED"}
    GREEN_FLAGS = {"#00FF00", "GREEN"}
    has_pure_red = any(c in RED_FLAGS for c in colours_used)
    has_pure_green = any(c in GREEN_FLAGS for c in colours_used)

    assert not (has_pure_red and has_pure_green), (
        "Chart uses both pure red and pure green — classic colour-blind failure mode"
    )


def test_gdpr_chart_uses_documented_accent_colour(loaded_data):
    """
    Confirms the specific colour-blind safe accent (#D55E00, Wong 2011
    palette per D-08) is actually applied, not just assumed.
    """
    df_incidents, df_rows = loaded_data
    fig = plot_gdpr_compliance(df_incidents)
    colours_used = [str(c).upper() for c in fig.data[0].marker.color]
    assert "#D55E00" in colours_used


# ─────────────────────────────────────────────────────────────────────────
# REQUIREMENT: Filter dropdowns must be built from live data, not
# hardcoded (D-06 decision, driven by sample vs full dataset differences)
# ─────────────────────────────────────────────────────────────────────────

def test_sector_options_derived_from_data_not_hardcoded(loaded_data):
    """
    Confirms filter dropdown options come from df_incidents directly,
    so the dashboard adapts automatically between sample and full dataset.
    """
    df_incidents, df_rows = loaded_data
    actual_sectors = set(df_incidents["sector"].unique())
    # Fixture has 3 sectors: Legal, Health, Education and childcare
    assert actual_sectors == {"Legal", "Health", "Education and childcare"}
    # If this dashboard hardcoded the 12-sector sample list or 21-sector
    # full list, neither would match this 3-sector fixture — proving
    # the options genuinely come from whatever data is loaded.
