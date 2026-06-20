# Chart Documentation

This document describes every chart rendered in the ICO Q1 2024 dashboard — what it shows, what the audience learns from it, and why that chart type was chosen over alternatives.

---

## Page 2 — Incident Types

### 1. Incident Types by Category (Horizontal Bar Chart)

**Function:** `plot_incident_type_by_category`

**What it shows**
All incident types ranked by frequency, with each bar coloured to indicate whether that incident type belongs to the Cyber or Non-Cyber category. The single largest incident type is outlined in black so the dominant cause is never lost visually.

**What the audience learns**

- Which specific incident types occur most frequently overall
- Whether high-frequency incident types are driven by human error (Non-Cyber) or deliberate attack (Cyber)
- That a single incident type tends to account for a disproportionate share of all reported incidents

**Why a horizontal bar chart**
Incident type labels are long text strings. A horizontal layout gives each label room to breathe without truncation or rotation. Ranking by frequency (ascending, so the longest bar is at the top) allows the eye to compare from most to least significant in a single scan. A stacked bar was considered but rejected — because each incident type belongs to exactly one category, stacking adds no information and removes the ability to read absolute counts per bar directly.

---

### 2. Breach Scale Profile — Cyber vs Non-Cyber (Line Chart)

**Function:** `plot_breach_scale_by_category`

**What it shows**
Two lines — one per category — tracing the distribution of breach scale (number of people affected) across ordered bands from "1 to 9" through "100k and above". The y-axis shows the percentage of incidents within each category, not raw counts.

**What the audience learns**

- Non-Cyber incidents peak sharply at the smallest band ("1 to 9"): most human-error breaches are small and contained
- Cyber incidents have a flatter profile that peaks in the middle bands ("100 to 1k"), meaning attacks more often affect larger numbers of people per incident
- The two lines cross early, confirming the categories have genuinely different scale profiles — not just different volumes

**Why a line chart (and why proportions, not counts)**
The bands are ordered categories, so connecting points with a line is meaningful — it traces the "shape" of each category's distribution, making peaks and crossovers immediately visible. A grouped bar chart was considered, but with seven bands and two groups, it becomes cluttered.

Proportions are used instead of raw counts because Non-Cyber incidents outnumber Cyber ~2.7:1. Plotting raw counts would make Cyber appear flat relative to Non-Cyber, hiding the genuine shape difference. Normalising to "% within each category" puts both on the same scale so the distribution profiles can be compared fairly.

---

## Page 3 — Sectoral Vulnerability

### 3. Sectoral Breach Volume (Stacked Horizontal Bar Chart)

**Function:** `plot_sectoral_vulnerability`

**What it shows**
Each sector as a horizontal bar split into two segments — Cyber incidents (one colour) and Non-Cyber incidents (another colour) — ranked by total incident count so the most-affected sector sits at the top.

**What the audience learns**

- Which sectors experience the highest overall volume of reported breaches
- How the Cyber/Non-Cyber split differs across sectors — some sectors are predominantly human-error-driven, others show a more even mix
- Relative magnitudes: a sector with a very long bar has far more incidents than one with a short bar

**Why a stacked horizontal bar chart**
The stacked layout encodes both total volume (total bar length) and category composition (segment proportions) in a single mark. A grouped bar would make totals harder to read; a 100% stacked bar would lose the absolute volume information, which is the primary question on this page.

---

### 4. Sector Impact — Frequency vs Estimated Scale (Bubble Chart)

**Function:** `plot_sector_impact_bubble`

**What it shows**
Each bubble represents one sector × category pair. Its horizontal position shows the incident count; its vertical position shows an estimated number of people affected, calculated by summing the conservative lower bound of each incident's subjects-affected band (e.g. "10k to 100k" → 10,000 per incident). Bubble size is proportional to estimated impact. Colour indicates Cyber vs Non-Cyber.

**What the audience learns**

- Sectors that appear modest by incident count can rank much higher by estimated impact — and vice versa
- Some sectors that rank high on the volume chart (Page 3 chart above) drop significantly when ranked by estimated harm
- Certain sectors show a near-even split between Cyber and Non-Cyber estimated impact, despite cyber incidents being numerically rarer, revealing that cyber-attacks in those sectors tend to affect more people per incident
- The overall share of estimated impact attributable to Cyber vs Non-Cyber (shown in the subtitle)

**Why a bubble chart**
The question requires two continuous measures to be read simultaneously: frequency and scale. A single-axis bar chart can only show one at a time. A scatter plot (two axes, no size encoding) would work but loses the visual emphasis on sectors with extreme impact. The bubble chart adds a third encoding (size) for the same impact measure, making outliers immediately visible without needing to read the axis precisely. Colour then adds the category dimension without adding a third axis.

**Important limitation**
The estimated impact figures are conservative lower bounds — the true number of people affected could be substantially higher within each band. This is stated explicitly in the chart subtitle.

---

## Page 4 — GDPR Compliance

### 5. GDPR Compliance by Sector (Horizontal Bar Chart)

**Function:** `plot_gdpr_compliance`

**What it shows**
Each sector's percentage of incidents reported to the ICO within the legally required 72-hour window (GDPR Article 33). Bars are ranked from lowest to highest compliance rate. The lowest-compliance sector is highlighted in orange, the highest in blue. A dashed vertical line marks the overall filtered average.

**What the audience learns**

- Which sectors are consistently late at reporting breaches
- The spread between the best and worst performing sectors
- How each sector compares to the overall average (the dashed reference line)
- Sample sizes (shown on each bar as `n=`) so small sectors can be identified and treated with appropriate caution

**Why a horizontal bar chart**
Sector names are long and benefit from a horizontal layout. The ranking (ascending) immediately directs the eye to the worst performer at the bottom and the best at the top. The dashed average line provides a reference baseline without adding a separate chart.

---

### 6. GDPR Compliance — Cyber vs Non-Cyber (Horizontal Bar Chart)

**Function:** `plot_gdpr_compliance_by_category`

**What it shows**
Two bars comparing the 72-hour compliance rate between Cyber and Non-Cyber incidents. Each bar is coloured by its category. A dashed line marks the overall average.

**What the audience learns**

- Whether human-error (Non-Cyber) incidents are also slower to report, compounding their already-dominant volume
- Whether cyber-attacks are handled more urgently (reported faster) or more slowly than non-cyber incidents
- Whether the compliance gap between categories is substantial or negligible

**Why a horizontal bar chart**
With only two categories, a bar chart is the simplest honest encoding. A pie chart would show composition but not make the rate comparison readable. A dot plot was considered but is most valuable when there are many categories clustered closely together — with two categories, bars are clearer.

---

### 7. GDPR Compliance Rate by Regulatory Decision (Dot Plot)

**Function:** `plot_gdpr_compliance_by_decision`

**What it shows**
One dot per regulatory decision type, positioned on a 0–100% axis showing that decision type's 72-hour compliance rate. A dashed vertical line shows the overall average.

**What the audience learns**

- Whether incidents that led to formal ICO action (e.g. "Investigation Pursued") were more or less likely to have been reported on time
- That all four decision types sit within a narrow range — the compliance rate does not obviously differentiate how the ICO responded

**Why a dot plot (not a bar chart)**
The finding here is that the rates are all close together. A bar chart would draw four long bars that look dramatically different even when the underlying values differ by only a few percentage points, because the eye compares bar lengths from zero. A dot plot anchors the comparison at the actual value positions, honestly communicating "these are all similar" when they are.

---

### 8. Compliance Gap by Regulatory Decision — Absolute Counts (Dumbbell Chart)

**Function:** `plot_gdpr_dumbbell_by_decision`

**What it shows**
For each regulatory decision type, two dots connected by a line: the left dot (orange) is the count of non-compliant incidents (reported late); the right dot (blue) is the count of compliant incidents (reported on time). The length of the connecting line is the absolute gap between the two.

**What the audience learns**

- The raw volume difference between compliant and non-compliant incidents per decision type — information the rate chart (Chart 7 above) cannot convey
- That "Informal Action Taken" dominates in absolute terms: its gap dwarfs those of other decision types, even though its compliance _rate_ looks similar to the rest
- A 60% compliance rate on 2,289 incidents represents a fundamentally different real-world situation than 60% on 130 incidents — the dumbbell makes this visible at a glance

**Why a dumbbell / connected dot plot**
This chart type is specifically designed for "two-group comparison per category" questions. A standard bar chart would show total incidents per decision, losing the compliant/non-compliant split. A stacked bar would show the split but make it hard to read the gap directly. A grouped bar chart works but makes it harder to perceive the gap as a single visual unit. The dumbbell turns the gap itself into a visible mark (the line segment), which is exactly the quantity of interest.
