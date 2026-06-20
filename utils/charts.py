# utils/charts.py
# Chart-building functions, imported by individual pages.

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.colours import (
    ACCENT, GREY, GREY_DARK,
    WORST_COLOUR, BEST_COLOUR,
    CATEGORY_COLOUR_MAP, BAND_COLOURS, BAND_ORDER,
)


# ─────────────────────────────────────────────────────────────────────────
# Cyber vs Non-Cyber Summary
# ─────────────────────────────────────────────────────────────────────────

def plot_category_summary(df_incidents):
    """Two-bar chart giving the instant Cyber vs Non-Cyber headline count."""
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=200)
        return fig

    counts = (
        df_incidents["category"]
        .value_counts()
        .reset_index()
    )
    counts.columns = ["category", "count"]
    counts = counts.sort_values("count", ascending=True).reset_index(drop=True)

    colours = counts["category"].map(CATEGORY_COLOUR_MAP)

    total = counts["count"].sum()
    labels = [
        f"{row.count:,}  ({row.count / total * 100:.0f}%)"
        for row in counts.itertuples()
    ]

    fig = go.Figure(
        go.Bar(
            x=counts["count"],
            y=counts["category"],
            orientation="h",
            marker_color=colours,
            text=labels,
            textposition="outside",
        )
    )

    dominant = counts.iloc[-1]["category"]
    dominant_pct = counts.iloc[-1]["count"] / total * 100

    fig.update_layout(
        title={
            "text": f"{dominant} Incidents Account for {dominant_pct:.0f}% of the Filtered Total  (n={total:,})",
            "x": 0.0,
            "xanchor": "left",
        },
        xaxis_title="Number of Incidents",
        yaxis_title=None,
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        showlegend=False,
        margin=dict(l=10, r=120, t=60, b=30),
        height=220,
    )

    return fig


# ─────────────────────────────────────────────────────────────────────────
# Incident Type Breakdown
# ─────────────────────────────────────────────────────────────────────────

def incident_type_counts(df_incidents):
    counts = df_incidents["incident_type"].value_counts().reset_index()
    counts.columns = ["incident_type", "count"]
    return counts


def plot_incident_type_breakdown(df_incidents, highlight_top_n=1):
    counts = incident_type_counts(df_incidents)
    counts = counts.sort_values("count", ascending=True).reset_index(drop=True)

    n = len(counts)
    colours = [GREY] * n
    for i in range(max(0, n - highlight_top_n), n):
        colours[i] = ACCENT

    fig = go.Figure(
        go.Bar(
            x=counts["count"],
            y=counts["incident_type"],
            orientation="h",
            marker_color=colours,
            text=counts["count"],
            textposition="outside",
        )
    )

    if n > 0:
        top_label = counts.iloc[-1]["incident_type"]
        top_value = counts.iloc[-1]["count"]
        total = counts["count"].sum()
        top_pct = (top_value / total) * 100 if total > 0 else 0
        title_text = (
            f"'{top_label}' Is the Leading Incident Type<br>"
            f"<sub>Accounts for {top_pct:.0f}% of filtered incidents (n={total})</sub>"
        )
    else:
        title_text = "No incidents match the current filters"

    fig.update_layout(
        title={"text": title_text, "x": 0.0, "xanchor": "left"},
        xaxis_title="Number of Incidents",
        yaxis_title=None,
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        showlegend=False,
        margin=dict(l=10, r=40, t=90, b=40),
        height=600,
    )

    return fig

def plot_incident_type_by_category(df_incidents):
    """
    Colours every bar by Cyber/Non-Cyber category (same palette as the
    Sectoral Vulnerability chart: orange = Cyber, blue = Non Cyber), so the
    human-error-vs-attack split is visible across the full ranked list, not
    just inferred from the single top bar. The single largest incident type
    keeps a bold outline so the "one dominant cause" finding isn't lost
    alongside the new category split.
    """
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=600)
        return fig

    counts = incident_type_counts(df_incidents)

    # Attach category — every incident_type maps to exactly one category
    cat_map = df_incidents.groupby("incident_type")["category"].first()
    counts["category"] = counts["incident_type"].map(cat_map)

    counts = counts.sort_values("count", ascending=True).reset_index(drop=True)

    colours = counts["category"].map(CATEGORY_COLOUR_MAP)

    # Outline only the single largest bar (last row, since ascending) so the
    # "one dominant incident type" finding from the original chart is retained
    n = len(counts)
    line_widths = [0] * n
    line_widths[-1] = 3
    line_colours = ["rgba(0,0,0,0)"] * n
    line_colours[-1] = "black"

    fig = go.Figure(
        go.Bar(
            x=counts["count"],
            y=counts["incident_type"],
            orientation="h",
            marker=dict(
                color=colours,
                line=dict(color=line_colours, width=line_widths),
            ),
            text=counts["count"],
            textposition="outside",
            customdata=counts["category"],
            hovertemplate="%{y}<br>%{customdata}: %{x} incidents<extra></extra>",
        )
    )

    total = counts["count"].sum()
    non_cyber_total = counts.loc[counts["category"] == "Non Cyber", "count"].sum()
    non_cyber_pct = (non_cyber_total / total) * 100 if total > 0 else 0

    # Manual legend via dummy traces, since a single bar trace can't show
    # a category legend on its own
    for cat, colour in CATEGORY_COLOUR_MAP.items():
        fig.add_trace(go.Bar(
            x=[None], y=[None],
            marker_color=colour,
            name=cat,
            showlegend=True,
        ))

    fig.update_layout(
        title={
            "text": f"Non-Cyber (Human Error) Incidents Dominate — {non_cyber_pct:.0f}% of All Incidents<br>"
                    "<sub>Bars coloured by category; outlined bar marks the single largest incident type</sub>",
            "x": 0.0,
            "xanchor": "left",
        },
        xaxis_title="Number of Incidents",
        yaxis_title=None,
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=40, t=110, b=40),
        height=50,
    )

    return fig

# ─────────────────────────────────────────────────────────────────────────
# Breach Scale by Category (Incident Types page)
# ─────────────────────────────────────────────────────────────────────────

def plot_breach_scale_by_category(df_incidents):
    """
    Line chart comparing the distribution of breach scale (subjects affected)
    between Cyber and Non-Cyber incidents, expressed as % within each category.
    Raw counts can't be compared directly because Non-Cyber incidents outnumber
    Cyber ~2.7:1; normalising to proportions reveals the shape difference —
    Non-Cyber peaks sharply at the smallest band (human errors are typically
    contained), while Cyber has a flatter profile skewed toward larger bands.
    """
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=400)
        return fig

    present_bands = [
        b for b in BAND_ORDER
        if b != "Unknown" and b in df_incidents["subjects_affected"].unique()
    ]

    counts = (
        df_incidents[df_incidents["subjects_affected"] != "Unknown"]
        .groupby(["category", "subjects_affected"])
        .size()
        .reset_index(name="count")
    )

    totals = counts.groupby("category")["count"].transform("sum")
    counts["pct"] = counts["count"] / totals * 100

    counts["subjects_affected"] = pd.Categorical(
        counts["subjects_affected"], categories=present_bands, ordered=True
    )
    counts = counts.sort_values(["category", "subjects_affected"])

    fig = go.Figure()
    for cat, colour in CATEGORY_COLOUR_MAP.items():
        subset = counts[counts["category"] == cat]
        if subset.empty:
            continue
        fig.add_trace(go.Scatter(
            x=subset["subjects_affected"].astype(str),
            y=subset["pct"],
            mode="lines+markers",
            name=cat,
            line=dict(color=colour, width=2.5),
            marker=dict(color=colour, size=8),
            customdata=subset["count"],
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "%{x}<br>"
                "%{y:.1f}% of category (%{customdata:,} incidents)"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title={
            "text": "Breach Scale Profile — Cyber vs Non-Cyber<br>"
                    "<sub>% of incidents within each category; Non-Cyber peaks at small scale, "
                    "Cyber is spread across larger bands</sub>",
            "x": 0.0,
            "xanchor": "left",
        },
        xaxis_title="People Affected",
        yaxis_title="% of Incidents (within category)",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(
            range=[0, counts["pct"].max()],
            showgrid=True, gridcolor="#EEEEEE", zeroline=False,
        ),
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=40, t=100, b=40),
        height=450,
    )

    return fig



# ─────────────────────────────────────────────────────────────────────────
# Sectoral Vulnerability
# ─────────────────────────────────────────────────────────────────────────

def sector_category_counts(df_incidents):
    counts = (
        df_incidents
        .groupby(["sector", "category"])
        .size()
        .reset_index(name="count")
    )
    return counts


def sector_order(df_incidents):
    totals = (
        df_incidents
        .groupby("sector")
        .size()
        .reset_index(name="total")
        .sort_values("total", ascending=True)
    )
    return totals["sector"].tolist()


def plot_sectoral_vulnerability(df_incidents):
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=700)
        return fig

    counts = sector_category_counts(df_incidents)
    order = sector_order(df_incidents)

    fig = px.bar(
        counts,
        x="count",
        y="sector",
        color="category",
        orientation="h",
        category_orders={"sector": order},
        color_discrete_map=CATEGORY_COLOUR_MAP,
        labels={"count": "Number of Incidents", "sector": "Sector", "category": "Incident Category"},
    )

    fig.update_layout(
        title="Sectoral Breach Volume — Filtered View",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        legend_title_text="",
        margin=dict(l=10, r=40, t=80, b=40),
        height=700,
    )

    return fig


def plot_sectoral_table(df_incidents):
    """Alternative view: cross-tab table instead of chart."""
    counts = sector_category_counts(df_incidents)
    pivot = counts.pivot(index="sector", columns="category", values="count").fillna(0).astype(int)
    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("Total", ascending=False)
    return pivot


# Conservative lower bound per subjects-affected band (used for estimated-impact charts)
BAND_LOWER_BOUNDS = {
    "1 to 9":         1,
    "10 to 99":       10,
    "100 to 1k":      100,
    "1k to 10k":      1_000,
    "10k to 100k":    10_000,
    "100k and above": 100_000,
}


def subjects_affected_by_sector(df_incidents, band_order):
    counts = (
        df_incidents[df_incidents["subjects_affected"] != "Unknown"]
        .groupby(["sector", "subjects_affected"])
        .size()
        .reset_index(name="count")
    )
    return counts


def plot_subjects_affected_by_sector(df_incidents, band_order):
    """
    Shows breach SCALE by sector (how many people affected), as distinct
    from breach VOLUME by sector (incident count, shown on the main
    Sectoral Vulnerability chart). A sector with few incidents but large
    breaches tells a different story than a sector with many small ones.
    """
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=700)
        return fig

    counts = subjects_affected_by_sector(df_incidents, band_order)
    order = sector_order(df_incidents)

    fig = px.bar(
        counts,
        x="count",
        y="sector",
        color="subjects_affected",
        orientation="h",
        category_orders={"sector": order, "subjects_affected": band_order},
        color_discrete_map=BAND_COLOURS,
        labels={"count": "Number of Incidents", "sector": "Sector", "subjects_affected": "People Affected"},
    )

    fig.update_layout(
        title="Breach Scale by Sector — Number of People Affected",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        legend_title_text="People Affected",
        margin=dict(l=10, r=40, t=80, b=40),
        height=700,
    )

    return fig


# ─────────────────────────────────────────────────────────────────────────
# GDPR Compliance by Sector
# ─────────────────────────────────────────────────────────────────────────

def gdpr_compliance_by_sector(df_incidents):
    summary = (
        df_incidents
        .groupby("sector")["gdpr_compliant"]
        .agg(total="count", compliant="sum")
        .reset_index()
    )
    summary["compliance_pct"] = (summary["compliant"] / summary["total"]) * 100
    return summary


def plot_gdpr_compliance(df_incidents):
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=700)
        return fig

    summary = gdpr_compliance_by_sector(df_incidents)
    summary = summary.sort_values("compliance_pct", ascending=True).reset_index(drop=True)

    n = len(summary)
    colours = [GREY] * n
    colours[0] = ACCENT

    labels = [
        f"{row.compliance_pct:.0f}%  (n={row.total})"
        for row in summary.itertuples()
    ]

    fig = go.Figure(
        go.Bar(
            x=summary["compliance_pct"],
            y=summary["sector"],
            orientation="h",
            marker_color=colours,
            text=labels,
            textposition="outside",
        )
    )

    worst_sector = summary.iloc[0]["sector"]
    worst_pct = summary.iloc[0]["compliance_pct"]
    overall_pct = (df_incidents["gdpr_compliant"].sum() / len(df_incidents)) * 100

    fig.update_layout(
        title={
            "text": f"{worst_sector} Lags Furthest Behind on GDPR 72-Hour Reporting<br>"
                    f"<sub>Just {worst_pct:.0f}% reported within the legal window (filtered view)</sub>",
            "x": 0.0,
            "xanchor": "left",
        },
        xaxis_title="% Reported Within 72 Hours",
        yaxis_title=None,
        xaxis=dict(range=[0, 110], showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=10, r=40, t=90, b=40),
        height=700,
    )

    fig.add_vline(
        x=overall_pct,
        line_dash="dash",
        line_color="black",
        annotation_text=f"Filtered avg: {overall_pct:.0f}%",
        annotation_position="top",
    )

    return fig


def gdpr_compliance_by_category(df_incidents):
    summary = (
        df_incidents
        .groupby("category")["gdpr_compliant"]
        .agg(total="count", compliant="sum")
        .reset_index()
    )
    summary["compliance_pct"] = (summary["compliant"] / summary["total"]) * 100
    return summary


def plot_gdpr_compliance_by_category(df_incidents):
    """
    Compares GDPR 72-hour compliance rate between Cyber and Non-Cyber
    incidents. Tests whether human-error (non-cyber) incidents, already
    shown to dominate by volume, are also worse at timely reporting —
    compounding the central Assignment 1 narrative.
    """
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=400)
        return fig

    summary = gdpr_compliance_by_category(df_incidents)
    summary = summary.sort_values("compliance_pct", ascending=True).reset_index(drop=True)

    colours = [CATEGORY_COLOUR_MAP.get(cat, GREY) for cat in summary["category"]]

    labels = [
        f"{row.compliance_pct:.0f}%  (n={row.total})"
        for row in summary.itertuples()
    ]

    fig = go.Figure(
        go.Bar(
            x=summary["compliance_pct"],
            y=summary["category"],
            orientation="h",
            marker_color=colours,
            text=labels,
            textposition="outside",
        )
    )

    overall_pct = (df_incidents["gdpr_compliant"].sum() / len(df_incidents)) * 100

    fig.update_layout(
        title="GDPR Compliance — Cyber vs Non-Cyber",
        xaxis_title="% Reported Within 72 Hours",
        yaxis_title=None,
        xaxis=dict(range=[0, 110], showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=10, r=40, t=60, b=40),
        height=300,
    )

    fig.add_vline(
        x=overall_pct,
        line_dash="dash",
        line_color="black",
        annotation_text=f"Avg: {overall_pct:.0f}%",
        annotation_position="top",
    )

    return fig


def gdpr_compliance_by_decision(df_incidents):
    summary = (
        df_incidents
        .groupby("decision")["gdpr_compliant"]
        .agg(total="count", compliant="sum")
        .reset_index()
    )
    summary["compliance_pct"] = (summary["compliant"] / summary["total"]) * 100
    return summary


def plot_gdpr_compliance_by_decision(df_incidents):
    """
    Tests whether the ICO's regulatory response correlates with whether the
    incident was reported on time — i.e. are late-reported breaches more
    likely to trigger formal action (Action Taken / Investigation Pursued)?

    Rendered as a dot plot rather than a bar chart (see D-25): the finding
    here is that compliance is similar across all four decision types
    (~7-point spread). A dot plot communicates "these are all close
    together" more honestly than a bar chart, where small differences
    between adjacent full-length bars can visually read as more dramatic
    than they are.
    """
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=350)
        return fig

    summary = gdpr_compliance_by_decision(df_incidents)
    summary = summary.sort_values("compliance_pct", ascending=True).reset_index(drop=True)

    GREY = GREY_DARK

    labels = [
        f"{row.compliance_pct:.0f}%  (n={row.total})"
        for row in summary.itertuples()
    ]

    overall_pct = (df_incidents["gdpr_compliant"].sum() / len(df_incidents)) * 100
    spread = summary["compliance_pct"].max() - summary["compliance_pct"].min()

    fig = go.Figure(
        go.Scatter(
            x=summary["compliance_pct"],
            y=summary["decision"],
            mode="markers+text",
            marker=dict(color=GREY, size=14, line=dict(width=0)),
            text=labels,
            textposition="middle right",
            textfont=dict(size=11),
        )
    )

    fig.update_layout(
        title={
            "text": "GDPR Compliance Rate by Regulatory Decision<br>"
                    f"<sub>All four decision types sit within a {spread:.0f}-point range — "
                    "no decision type stands out</sub>",
            "x": 0.0,
            "xanchor": "left",
        },
        xaxis_title="% Reported Within 72 Hours",
        yaxis_title=None,
        xaxis=dict(range=[0, 100], showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=10, r=110, t=90, b=40),
        height=350,
    )

    fig.add_vline(
        x=overall_pct,
        line_dash="dash",
        line_color="black",
        annotation_text=f"Avg: {overall_pct:.0f}%",
        annotation_position="top",
    )

    return fig


def gdpr_compliance_by_subjects_affected(df_incidents, band_order):
    summary = (
        df_incidents
        .groupby("subjects_affected")["gdpr_compliant"]
        .agg(total="count", compliant="sum")
        .reset_index()
    )
    summary["compliance_pct"] = (summary["compliant"] / summary["total"]) * 100
    # Apply canonical band order (D-15) rather than relying on groupby's default sort
    summary["subjects_affected"] = pd.Categorical(
        summary["subjects_affected"], categories=band_order, ordered=True
    )
    summary = summary.sort_values("subjects_affected").reset_index(drop=True)
    return summary


def plot_gdpr_compliance_by_subjects_affected(df_incidents, band_order):
    """
    Tests whether breach scale (people affected) relates to GDPR reporting
    compliance. NOTE: on initial exploration this relationship was found to
    be non-monotonic (no smooth "bigger breach = later report" gradient),
    and the largest band typically has the smallest sample size — both are
    surfaced directly in the chart rather than smoothed over.
    """
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=400)
        return fig

    summary = gdpr_compliance_by_subjects_affected(df_incidents, band_order)

    # Highlight whichever band has the lowest compliance, wherever it falls
    colours = [GREY] * len(summary)
    worst_idx = summary["compliance_pct"].idxmin()
    colours[worst_idx] = ACCENT

    labels = [
        f"{row.compliance_pct:.0f}%  (n={row.total})"
        for row in summary.itertuples()
    ]

    fig = go.Figure(
        go.Bar(
            x=summary["subjects_affected"].astype(str),
            y=summary["compliance_pct"],
            marker_color=colours,
            text=labels,
            textposition="outside",
        )
    )

    overall_pct = (df_incidents["gdpr_compliant"].sum() / len(df_incidents)) * 100

    fig.update_layout(
        title={
            "text": "GDPR Compliance by Breach Scale<br>"
                    "<sub>No smooth trend with scale — smallest sample sizes "
                    "sit at the larger end, shown via n=</sub>",
            "x": 0.0,
            "xanchor": "left",
        },
        xaxis_title="People Affected",
        yaxis_title="% Reported Within 72 Hours",
        yaxis=dict(range=[0, 85], showgrid=False, zeroline=False),
        xaxis=dict(showgrid=False),
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=10, r=40, t=90, b=40),
        height=450,
    )

    fig.add_hline(
        y=overall_pct,
        line_dash="dash",
        line_color="black",
        annotation_text=f"Avg: {overall_pct:.0f}%",
        annotation_position="right",
    )

    return fig


def plot_gdpr_compliance_dotplot(df_incidents):
    """Alternative view: dot plot with worst/best highlighted."""
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=700)
        return fig

    summary = gdpr_compliance_by_sector(df_incidents)
    summary = summary.sort_values("compliance_pct", ascending=True).reset_index(drop=True)

    n = len(summary)
    colours = [GREY] * n
    colours[0] = WORST_COLOUR
    colours[-1] = BEST_COLOUR

    sizes = [10] * n
    sizes[0] = 16
    sizes[-1] = 16

    labels = [f"{row.compliance_pct:.0f}%  (n={row.total})" for row in summary.itertuples()]

    fig = go.Figure(
        go.Scatter(
            x=summary["compliance_pct"],
            y=summary["sector"],
            mode="markers+text",
            marker=dict(color=colours, size=sizes, line=dict(width=0)),
            text=labels,
            textposition="middle right",
            textfont=dict(size=11),
        )
    )

    worst_sector = summary.iloc[0]["sector"]
    worst_pct = summary.iloc[0]["compliance_pct"]
    best_sector = summary.iloc[-1]["sector"]
    best_pct = summary.iloc[-1]["compliance_pct"]
    overall_pct = (df_incidents["gdpr_compliant"].sum() / len(df_incidents)) * 100

    fig.update_layout(
        title={
            "text": f"GDPR Compliance Ranges From {worst_pct:.0f}% to {best_pct:.0f}% Across Sectors<br>"
                    f"<sub>{worst_sector} lags furthest behind; {best_sector} leads</sub>",
            "x": 0.0,
            "xanchor": "left",
        },
        xaxis_title="% Reported Within 72 Hours",
        yaxis_title=None,
        xaxis=dict(range=[0, 115], showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=10, r=40, t=90, b=40),
        height=700,
    )

    fig.add_vline(
        x=overall_pct,
        line_dash="dash",
        line_color="black",
        annotation_text=f"Avg: {overall_pct:.0f}%",
        annotation_position="top",
    )

    return fig


# ─────────────────────────────────────────────────────────────────────────
# Sector Impact Bubble Chart (frequency × estimated scale)
# ─────────────────────────────────────────────────────────────────────────

def plot_sector_impact_bubble(df_incidents):
    """
    Bubble chart: X = incident count, Y = estimated people affected (lower-bound
    sum of each band), bubble size ∝ estimated impact, colour = category.

    Each point is one sector × category pair, so a sector appears as two bubbles
    (Cyber and Non-Cyber) revealing whether its impact is driven by frequency or
    by scale — a distinction the original incident-count bar chart cannot make.

    'Estimated' is stated explicitly: the true figure could be substantially
    higher since we use each band's lower bound (e.g. "10k to 100k" → 10,000).
    """
    if len(df_incidents) == 0:
        fig = go.Figure()
        fig.update_layout(title="No incidents match the current filters", height=500)
        return fig

    df_known = df_incidents[df_incidents["subjects_affected"] != "Unknown"].copy()
    df_known["est_affected"] = df_known["subjects_affected"].map(BAND_LOWER_BOUNDS)

    summary = (
        df_known.groupby(["sector", "category"])
        .agg(
            incident_count=("est_affected", "count"),
            est_affected=("est_affected", "sum"),
        )
        .reset_index()
    )

    total_est = summary["est_affected"].sum()
    cyber_pct = (
        summary.loc[summary["category"] == "Cyber", "est_affected"].sum()
        / total_est * 100
        if total_est > 0 else 0
    )

    max_est = summary["est_affected"].max()
    sizeref = 2.0 * max_est / (60 ** 2)

    fig = go.Figure()

    for cat, colour in CATEGORY_COLOUR_MAP.items():
        subset = summary[summary["category"] == cat].reset_index(drop=True)
        if subset.empty:
            continue
        fig.add_trace(go.Scatter(
            x=subset["incident_count"],
            y=subset["est_affected"],
            mode="markers",
            name=cat,
            marker=dict(
                color=colour,
                size=subset["est_affected"],
                sizemode="area",
                sizeref=sizeref,
                sizemin=6,
                opacity=0.75,
                line=dict(color="white", width=1),
            ),
            text=subset["sector"],
            hovertemplate=(
                "<b>%{text}</b> — %{fullData.name}<br>"
                "Incidents: %{x:,}<br>"
                "Est. people affected: %{y:,}<br>"
                "<i>Lower-bound estimate</i>"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title={
            "text": (
                "Sector Impact — Incident Frequency vs Estimated Scale<br>"
                f"<sub>Bubble size = est. people affected (lower-bound sum); "
                f"Cyber accounts for {cyber_pct:.1f}% of total estimated impact. "
                f"Estimates are conservative — true figures may be substantially higher.</sub>"
            ),
            "x": 0.0,
            "xanchor": "left",
        },
        xaxis_title="Incident Count",
        yaxis_title="Est. People Affected (lower-bound sum)",
        plot_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#EEEEEE", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#EEEEEE", zeroline=False),
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=40, t=120, b=40),
        height=560,
    )

    return fig

