# Requirements Traceability — Functional & Non-Functional Testing

This document complements `tests/test_functional_requirements.py`. Some
requirements from the Assignment 1 design plan can be verified automatically
in code; others — particularly those concerning the rendered UI, human
usability, or subjective visual judgement — cannot, and are verified
manually instead. Both are recorded here so the testing coverage is
complete and honest about its own limits, not just the parts that were
easy to automate.

**Verification methods used:**
- **Automated** — covered by a pytest test in `tests/`
- **Manual** — checked by running the app and observing it directly
- **Not yet verified** — identified as a requirement but not yet checked

---

## Functional Requirements

| Requirement (Assignment 1) | Verification Method | Result |
|---|---|---|
| Interactive filtering by sector, incident type, incident category, time taken to report | Automated — `test_all_four_planned_filter_fields_are_supported`, plus one narrowing test per field | Pass |
| All charts update simultaneously when filters change | Automated (chart output reflects filtered input) + Manual (visually confirmed in browser across all three chart pages) | Pass |
| Sector and Incident Type visualised via bar charts | Automated — chart functions tested directly | Pass |
| GDPR Compliance View highlights 72-hour reporting requirement | Automated — `test_gdpr_compliance_threshold_matches_72_hour_rule` | Pass |
| Dashboard summarises Q1 2024 incidents | Manual — Home and Narrative pages reviewed for accuracy against `load_data()` output | Pass |

---

## Non-Functional Requirements

| Requirement (Assignment 1) | Verification Method | Result |
|---|---|---|
| Trustworthy — visualisations accurately represent underlying data, no distortion | Automated — Category 1 data integrity suite (`test_data_integrity.py`), 25 tests | Pass |
| Accessible — colour-blind safe palettes | Automated (partial — checks for known red/green failure mode and confirms documented accent colour is applied) + Manual (visual review; full colour-blindness simulation not performed) | Pass (automated scope); simulation tool not yet used |
| Accessible — plain English labels, no jargon | Manual — chart titles and axis labels reviewed against ICO glossary terminology | Pass |
| Operable by a non-technical user within five minutes, without training | **Not yet verified** — requires a usability walkthrough with someone unfamiliar with the project, not yet conducted | Pending |
| Performance — responds to filter interactions within three seconds | Automated (partial — measures function execution time for filter + chart build, not full browser round-trip) + Manual (subjectively felt instant when tested locally) | Pass (automated scope) |
| Deployable on standard desktop environments without specialist configuration | Manual — run via `streamlit run app.py` on a standard machine with `pip install` dependencies only | Pass |

---

## Known Gaps

Two items in this table are not fully closed out and are worth being upfront
about rather than marking as complete:

1. **Five-minute non-technical usability** — this requirement is inherently
   about human perception and cannot be meaningfully unit-tested. A short
   walkthrough with someone outside the project (e.g. a coursemate or
   family member unfamiliar with the dataset) would be needed to genuinely
   verify this, timing how long it takes them to find a specific finding
   unaided.

2. **Full colour-blindness simulation** — the automated test only catches
   the specific, well-known red/green failure mode. A proper check would
   run the rendered dashboard through a colour-blindness simulator (e.g.
   Coblis, or a browser extension) covering deuteranopia, protanopia, and
   tritanopia, rather than relying on the palette's documented design
   intent (Wong, 2011) alone.

Both gaps are noted here as a deliberate scope decision for this stage of
the prototype, rather than silently omitted from the testing section of
the write-up.
