DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --bg: #07090f;
  --surface: #0e1117;
  --surface2: #161b27;
  --border: #1f2937;
  --text: #e8eaf6;
  --muted: #6b7280;
}

html, body, [class*="css"] {
  font-family: 'Inter', system-ui, sans-serif !important;
}

.stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* ── RAINBOW TEXT (gradient inside the letters) ──────────────── */
@keyframes rainbowFlow {
  0%   { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

.rainbow-text {
  background: linear-gradient(
    90deg,
    #ff0000, #ff7700, #ffee00, #00ff88,
    #00cfff, #7700ff, #ff00cc, #ff0000
  );
  background-size: 300% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: rainbowFlow 2s linear infinite;
  font-weight: 900 !important;
  display: inline-block;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: #0b0d14 !important;
  border-right: 1px solid #1a1f2e !important;
}
section[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
section[data-testid="stSidebar"] p { color: #4b5563 !important; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { visibility: hidden !important; }

/* Headings */
h1 { color: var(--text) !important; font-weight: 900 !important; }
h2, h3 { color: var(--text) !important; font-weight: 700 !important; }
h4, h5, h6 { color: var(--text) !important; }
p, span, label { color: var(--text) !important; }

/* Metric cards */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 1rem 1.25rem !important;
}
[data-testid="stMetric"] label {
  color: var(--muted) !important;
  font-size: .72rem !important;
  text-transform: uppercase !important;
  letter-spacing: .08em !important;
}
[data-testid="stMetricValue"] {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 1.75rem !important;
  font-weight: 700 !important;
  color: var(--text) !important;
}

/* Tabs */
[data-testid="stTabs"] button {
  background: transparent !important;
  color: var(--muted) !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  font-weight: 600 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: #38bdf8 !important;
  border-bottom-color: #38bdf8 !important;
  background: transparent !important;
}

/* Buttons */
.stButton > button {
  background: linear-gradient(90deg, #6366f1, #38bdf8) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
  padding: .55rem 1.5rem !important;
  transition: all .2s !important;
  letter-spacing: .01em !important;
}
.stButton > button:hover {
  opacity: .9 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(99,102,241,.35) !important;
}
.stDownloadButton > button {
  background: rgba(56,189,248,.08) !important;
  color: #38bdf8 !important;
  border: 1px solid rgba(56,189,248,.3) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
}

/* Inputs & Selects — force dark everywhere */
.stTextInput input, .stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  background: #161b27 !important;
  border: 1px solid #1f2937 !important;
  border-radius: 8px !important;
  color: #e8eaf6 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: #38bdf8 !important;
  box-shadow: 0 0 0 2px rgba(56,189,248,.12) !important;
}

/* Select boxes — every layer dark */
[data-baseweb="select"] { background: #161b27 !important; border-radius: 8px !important; }
[data-baseweb="select"] > div { background: #161b27 !important; border: 1px solid #1f2937 !important; border-radius: 8px !important; color: #e8eaf6 !important; }
[data-baseweb="select"] input { background: #161b27 !important; color: #e8eaf6 !important; }
[data-baseweb="select"] span { color: #e8eaf6 !important; }
[data-baseweb="select"] svg { fill: #6b7280 !important; }

/* Dropdown popover/menu */
[data-baseweb="popover"] { background: #0e1117 !important; border: 1px solid #1f2937 !important; border-radius: 10px !important; box-shadow: 0 8px 32px rgba(0,0,0,.6) !important; }
[data-baseweb="menu"] { background: #0e1117 !important; }
[data-baseweb="menu"] ul { background: #0e1117 !important; padding: 4px !important; }
li[role="option"] { background: #0e1117 !important; color: #e8eaf6 !important; border-radius: 6px !important; }
li[role="option"]:hover { background: #161b27 !important; }
li[role="option"][aria-selected="true"] { background: rgba(56,189,248,.12) !important; color: #38bdf8 !important; }

/* Number input */
[data-baseweb="input"] { background: #161b27 !important; border: 1px solid #1f2937 !important; border-radius: 8px !important; }
[data-testid="stNumberInput"] input { background: #161b27 !important; color: #e8eaf6 !important; }
[data-testid="stNumberInput"] button { background: #1f2937 !important; color: #6b7280 !important; border: none !important; }

/* Checkbox & Radio */
[data-testid="stCheckbox"] label span, [data-testid="stRadio"] label span { color: #e8eaf6 !important; }
[data-testid="stCheckbox"] input + span, [data-testid="stRadio"] input + span {
  background: #161b27 !important; border-color: #1f2937 !important;
}

/* Slider track */
[data-testid="stSlider"] [data-baseweb="slider"] div { background: #1f2937 !important; }
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { background: #38bdf8 !important; border-color: #38bdf8 !important; }

/* Tooltip */
[data-baseweb="tooltip"] div { background: #0e1117 !important; border: 1px solid #1f2937 !important; color: #e8eaf6 !important; border-radius: 8px !important; }

/* File uploader — kill all white */
[data-testid="stFileUploader"] { background: transparent !important; border: none !important; }
[data-testid="stFileUploaderDropzone"] {
  background: #0e1117 !important;
  border: 2px dashed rgba(56,189,248,.25) !important;
  border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: #38bdf8 !important;
  background: rgba(56,189,248,.04) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { color: #6b7280 !important; }
[data-testid="stFileUploaderDropzoneInstructions"] span { color: #6b7280 !important; }
[data-testid="stFileUploaderDropzoneInstructions"] svg { fill: #374151 !important; }
[data-testid="stFileUploader"] button {
  background: rgba(56,189,248,.1) !important;
  color: #38bdf8 !important;
  border: 1px solid rgba(56,189,248,.3) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
}
[data-testid="stFileUploader"] small { color: #4b5563 !important; }

/* Dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}

/* Expander */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; font-weight: 600 !important; }

/* Multiselect */
[data-baseweb="tag"] {
  background: rgba(56,189,248,.12) !important;
  color: #38bdf8 !important;
  border-radius: 999px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1f2937; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #38bdf8; }

.js-plotly-plot { background: transparent !important; }
</style>
"""

SIDEBAR_CSS = """
<style>
@keyframes rainbowFlow {
  0%   { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

.sidebar-logo {
  display: flex; align-items: center; gap: .55rem;
  padding: 1rem 0 1.4rem;
  border-bottom: 1px solid #1a1f2e;
  margin-bottom: 1rem;
}
.sidebar-logo-icon {
  font-size: 1.6rem;
  background: linear-gradient(90deg,#ff0000,#ff7700,#ffee00,#00ff88,#00cfff,#7700ff,#ff00cc,#ff0000);
  background-size: 300% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: rainbowFlow 2s linear infinite;
}
.sidebar-logo-text {
  font-size: 1.1rem; font-weight: 800; color: #e8eaf6; letter-spacing: -.4px;
}
.sidebar-logo-text span {
  background: linear-gradient(90deg,#6366f1,#38bdf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.ds-card {
  background: rgba(56,189,248,.06);
  border: 1px solid rgba(56,189,248,.15);
  border-radius: 10px;
  padding: .7rem .95rem;
  margin-bottom: 1.2rem;
}
.ds-card-name { font-size: .8rem; font-weight: 700; color: #e8eaf6; }
.ds-card-stats { font-size: .7rem; color: #38bdf8; margin-top: 2px; }
.ds-card-empty { border-color: #1f2937; background: transparent; }
.ds-card-empty .ds-card-name { color: #4b5563; }
.ds-card-empty .ds-card-stats { color: #374151; }
</style>
"""


def kpi_row_html(stats: list) -> str:
    colors = ["#f472b6", "#fb923c", "#facc15", "#4ade80", "#38bdf8", "#a78bfa"]
    cards = ""
    for i, (label, value) in enumerate(stats):
        c = colors[i % len(colors)]
        cards += f"""
        <div style="background:#0e1117;border:1px solid #1f2937;border-radius:12px;
                    padding:1rem 1.25rem;position:relative;overflow:hidden;flex:1;min-width:120px;">
          <div style="position:absolute;top:0;left:0;right:0;height:2px;background:{c};"></div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:1.6rem;font-weight:700;
                      color:{c};">{value}</div>
          <div style="font-size:.68rem;color:#6b7280;text-transform:uppercase;
                      letter-spacing:.08em;margin-top:.15rem;">{label}</div>
        </div>"""
    return f'<div style="display:flex;gap:.65rem;flex-wrap:wrap;margin:1rem 0;">{cards}</div>'


def section_header(icon: str, title: str, subtitle: str = "") -> str:
    sub = f'<div style="color:#6b7280;font-size:.86rem;margin-top:.2rem;">{subtitle}</div>' if subtitle else ""
    return f"""
    <div style="margin-bottom:1.5rem;padding-bottom:.9rem;border-bottom:1px solid #1f2937;">
      <div style="display:flex;align-items:center;gap:.55rem;">
        <span style="font-size:1.3rem;">{icon}</span>
        <h2 style="margin:0;font-size:1.35rem;font-weight:700;color:#e8eaf6;">{title}</h2>
      </div>
      {sub}
    </div>"""


def badge(text: str, color: str = "sky") -> str:
    colors = {
        "sky":    ("rgba(56,189,248,.12)",  "#38bdf8"),
        "indigo": ("rgba(99,102,241,.12)",  "#818cf8"),
        "pink":   ("rgba(244,114,182,.12)", "#f472b6"),
        "green":  ("rgba(74,222,128,.12)",  "#4ade80"),
        "amber":  ("rgba(250,204,21,.12)",  "#facc15"),
        "red":    ("rgba(248,113,113,.12)", "#f87171"),
        "gray":   ("rgba(107,114,128,.10)", "#6b7280"),
    }
    bg, fg = colors.get(color, colors["gray"])
    return f'<span style="background:{bg};color:{fg};padding:.2rem .6rem;border-radius:999px;font-size:.7rem;font-weight:600;font-family:monospace;">{text}</span>'
