# utils/colours.py
# Central palette — edit here to restyle the entire dashboard.

# Category colours (colour-blind safe)
CYBER     = "#0072B2"   
NON_CYBER = "#D55E00" 

# Neutral tones
GREY      = "#767676"  
GREY_DARK = "#707070" 

# Convenience aliases used inside chart functions
ACCENT       = CYBER
WORST_COLOUR = CYBER
BEST_COLOUR  = NON_CYBER

# Category → colour mapping (passed directly to Plotly color_discrete_map)
CATEGORY_COLOUR_MAP = {
    "Cyber":     CYBER,
    "Non Cyber": NON_CYBER,
}

# Sequential blue palette for "subjects affected" bands (medium → dark = small → large).
# Light blues (#DDEEFF, #A6CEE3) failed WCAG 1.4.11 (< 3:1 on white), so the scale
# starts at medium-blue and darkens — all five steps now pass 3:1 on white.
BAND_COLOURS = {
    "1 to 9":         "#4393C3",  # 3.1:1
    "10 to 99":       "#3282B5",  # 3.9:1
    "100 to 1k":      "#2373A8",  # 4.7:1
    "1k to 10k":      "#2166AC",  # 5.4:1
    "10k to 100k":    "#053061",  # 11.8:1
    "100k and above": "#021A35",  # 19.5:1 — extreme-scale breaches
    "Unknown":        "#767676",  # 4.5:1  — reuses GREY; no scale meaning
}

BAND_ORDER = [
    "1 to 9", "10 to 99", "100 to 1k",
    "1k to 10k", "10k to 100k", "100k and above", "Unknown",
]
