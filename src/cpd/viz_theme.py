COLOR_PALETTE = {
    "primary": "#8F1D2C",
    "dark": "#6F1420",
    "secondary": "#B5495B",
    "positive": "#3F7D4E",
    "warning": "#A15A1C",
    "neutral": "#8A8178",
    "accent": "#C9A27A",
    "cream": "#F7F1E8",
    "card": "#FFF9F2",
    "white": "#FFFFFF",
    "text": "#222222",
    "text_secondary": "#666666",
    "border": "#E6DDD2",
}

FONT_RULES = {
    "family": "Arial, Helvetica, Tahoma, 'Leelawadee UI', 'Noto Sans Thai', Sarabun, Thonburi, sans-serif",
    "title_size": 32,
    "subtitle_size": 14,
    "body_size": 14,
    "kpi_value_size": 30,
    "kpi_label_size": 14,
}

CHART_DEFAULTS = {
    "show_legend": False,
    "show_grid": True,
    "animation": False,
    "responsive": True,
    "empty_state_text": "No data available for the current filter.",
}


def build_css() -> str:
    """Presentation-only stylesheet (no animation/transition). Built from the palette above."""
    p, f = COLOR_PALETTE, FONT_RULES
    return f"""
<style>
html, body, [class*="css"], .stApp {{ font-family: {f['family']}; font-size: {f['body_size']}px; color: {p['text']}; }}
.stApp {{ background: {p['cream']}; }}
header[data-testid="stHeader"] {{ background: {p['cream']}; }}
.st-key-langbar {{ display: flex; justify-content: flex-end; margin-bottom: .25rem; }}
.st-key-langbar [data-testid="stRadio"] {{ width: auto; margin-left: auto; }}
.st-key-langbar [data-testid="stRadio"] > label p {{ font-weight: 700; color: {p['dark']}; }}
.st-key-langbar [role="radiogroup"] {{ gap: .5rem; }}
.st-key-langbar [role="radiogroup"] label {{ background: #FFFFFF; border: 2px solid {p['primary']}; border-radius: 999px; padding: .15rem .9rem; }}
.st-key-langbar [role="radiogroup"] label:has(input:checked) {{ background: {p['primary']}; }}
.st-key-langbar [role="radiogroup"] label:has(input:checked) * {{ color: #FFFFFF !important; }}
.st-key-langbar [role="radiogroup"] label:focus-within {{ outline: 3px solid {p['dark']}; outline-offset: 2px; }}
.block-container {{ max-width: 1200px; padding-top: 4rem; padding-bottom: 4rem; }}
* {{ animation: none !important; transition: none !important; }}
h2, h3 {{ color: {p['dark']}; font-weight: 700; letter-spacing: 0; margin-top: 2rem; }}

.cpd-header {{ background: {p['primary']}; color: #FFFFFF; border-radius: 12px; padding: 1.75rem 2rem; margin-bottom: 1.5rem; border-bottom: 6px solid {p['dark']}; }}
.cpd-header .cpd-eyebrow {{ font-size: {f['subtitle_size']}px; letter-spacing: .08em; text-transform: uppercase; opacity: .95; margin: 0 0 .25rem 0; }}
.cpd-header h1 {{ color: #FFFFFF; font-size: {f['title_size']}px; font-weight: 800; line-height: 1.2; margin: 0 0 .5rem 0; padding: 0; }}
.cpd-header p {{ font-size: {f['subtitle_size'] + 2}px; margin: 0; }}
.cpd-pill {{ display: inline-block; background: #FFFFFF; color: {p['dark']}; border-radius: 999px; padding: .1rem .75rem; font-weight: 700; margin-left: .25rem; }}

[data-testid="stMetric"] {{ background: #FFFFFF; border: 1px solid {p['border']}; border-left: 6px solid {p['primary']}; border-radius: 10px; padding: 1rem 1.25rem; box-shadow: 0 1px 3px rgba(34,34,34,.10); }}
[data-testid="stMetricLabel"] p {{ font-size: {f['kpi_label_size'] + 1}px; font-weight: 600; color: #444444; }}
[data-testid="stMetricValue"] {{ font-size: {f['kpi_value_size'] + 6}px; font-weight: 800; color: {p['dark']}; }}

.st-key-filter, .st-key-stage, .st-key-drill, .st-key-aging {{ background: #FFFFFF; border: 1px solid {p['border']}; border-radius: 12px; padding: 1.25rem 1.5rem; margin-top: 1rem; }}
.st-key-top3 {{ background: {p['card']}; border: 1px solid {p['border']}; border-top: 6px solid {p['primary']}; border-radius: 12px; padding: 1.25rem 1.5rem; margin-top: 1.5rem; }}
.st-key-ai {{ background: {p['card']}; border: 1px solid {p['border']}; border-radius: 12px; padding: 1.25rem 1.5rem; margin-top: 1.5rem; }}
.st-key-ai h3, .st-key-top3 h3 {{ color: {p['primary']}; margin-top: 0; }}
.st-key-filter label p {{ font-weight: 700; color: {p['dark']}; }}
div[data-baseweb="select"] > div {{ background: #FFFFFF; border: 2px solid {p['primary']}; color: {p['text']}; }}
div[data-baseweb="select"] > div:focus-within {{ outline: 3px solid {p['dark']}; outline-offset: 2px; }}
.stButton button {{ background: {p['primary']}; color: #FFFFFF; border: 2px solid {p['dark']}; font-weight: 700; padding: .5rem 1.25rem; }}
.stButton button:hover {{ background: {p['dark']}; color: #FFFFFF; }}
.stButton button:focus-visible {{ outline: 3px solid {p['dark']}; outline-offset: 2px; }}
.stButton button:disabled {{ background: #E6DDD2; color: #444444; border-color: {p['border']}; }}

.cpd-rank-card {{ background: #FFFFFF; border: 1px solid {p['border']}; border-radius: 10px; padding: 1rem 1.25rem; height: 100%; }}
.cpd-rank-num {{ display: inline-block; background: {p['primary']}; color: #FFFFFF; font-weight: 800; font-size: 1.4rem; border-radius: 8px; padding: .1rem .7rem; margin-bottom: .5rem; }}
.cpd-rank-card .cpd-days {{ font-size: 2rem; font-weight: 800; color: {p['dark']}; line-height: 1.1; }}
.cpd-rank-card .cpd-meta {{ color: #444444; font-size: {f['body_size'] + 1}px; line-height: 1.6; margin-top: .4rem; }}
.cpd-brief {{ background: #FFFFFF; border: 1px solid {p['border']}; border-radius: 10px; padding: 1rem 1.25rem; font-size: {f['body_size'] + 2}px; line-height: 1.75; }}
[data-testid="stMetricLabel"] p, [data-testid="stMetricValue"], .stButton button, .cpd-meta, .cpd-header p {{ overflow-wrap: anywhere; white-space: normal; line-height: 1.5; }}
.stButton button {{ height: auto; min-height: 2.5rem; }}
h2, h3 {{ line-height: 1.4; }}
[data-testid="stCaptionContainer"] {{ color: {p['text_secondary']}; }}
</style>
"""
