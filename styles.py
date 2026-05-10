DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #060B1A;
  --surface: #0D1528;
  --surface2: #111827;
  --border: #1E293B;
  --border2: #2D3748;
  --text: #E2E8F0;
  --text-muted: #94A3B8;
  --cyan: #00D4FF;
  --purple: #7C3AED;
  --pink: #FF006E;
  --green: #10B981;
  --amber: #F59E0B;
  --red: #EF4444;
}

html, body, [class*="css"] {
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
}

.stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
  color: var(--text) !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] p {
  color: var(--text-muted) !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { visibility: hidden !important; }

/* Headings */
h1 { color: var(--text) !important; font-size: 2rem !important; font-weight: 700 !important; }
h2 { color: var(--text) !important; font-weight: 600 !important; }
h3 { color: var(--text) !important; font-weight: 600 !important; }
h4, h5, h6 { color: var(--text) !important; }
p, span, label { color: var(--text) !important; }

/* Metric cards */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 1rem 1.25rem !important;
}
[data-testid="stMetric"] label {
  color: var(--text-muted) !important;
  font-size: .75rem !important;
  text-transform: uppercase !important;
  letter-spacing: .05em !important;
}
[data-testid="stMetricValue"] {
  color: var(--cyan) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 1.8rem !important;
}
[data-testid="stMetricDelta"] { font-size: .8rem !important; }

/* Tabs */
[data-testid="stTabs"] button {
  background: transparent !important;
  color: var(--text-muted) !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  font-weight: 500 !important;
  transition: all .2s !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom-color: var(--cyan) !important;
  background: transparent !important;
}
[data-testid="stTabs"] [data-testid="stMarkdownContainer"] p {
  color: var(--text) !important;
}

/* Buttons */
.stButton > button {
  background: var(--cyan) !important;
  color: #000 !important;
  border: none !important;
  border-radius: 6px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  padding: .5rem 1.25rem !important;
  transition: all .2s !important;
}
.stButton > button:hover {
  opacity: .9 !important;
  transform: translateY(-1px) !important;
}
.stDownloadButton > button {
  background: rgba(0,212,255,.1) !important;
  color: var(--cyan) !important;
  border: 1px solid rgba(0,212,255,.3) !important;
  border-radius: 6px !important;
  font-weight: 600 !important;
}

/* Inputs / Selects */
.stTextInput input, .stTextArea textarea, .stSelectbox select,
[data-baseweb="select"] div, [data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
  color: var(--text) !important;
  font-family: 'Space Grotesk', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 2px rgba(0,212,255,.1) !important;
}
[data-baseweb="select"] { background: var(--surface2) !important; }

/* File uploader */
[data-testid="stFileUploader"] {
  background: rgba(0,212,255,.03) !important;
  border: 2px dashed rgba(0,212,255,.25) !important;
  border-radius: 10px !important;
  padding: 2rem !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--cyan) !important;
  background: rgba(0,212,255,.06) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}

/* Alerts */
[data-testid="stAlert"] {
  border-radius: 8px !important;
  border-left: 4px solid !important;
}
[data-testid="stAlert"][kind="info"] { border-left-color: var(--cyan) !important; background: rgba(0,212,255,.06) !important; }
[data-testid="stAlert"][kind="success"] { border-left-color: var(--green) !important; background: rgba(16,185,129,.06) !important; }
[data-testid="stAlert"][kind="warning"] { border-left-color: var(--amber) !important; background: rgba(245,158,11,.06) !important; }
[data-testid="stAlert"][kind="error"] { border-left-color: var(--red) !important; background: rgba(239,68,68,.06) !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Expander */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
  color: var(--text) !important;
  font-weight: 600 !important;
}

/* Multiselect */
[data-baseweb="tag"] {
  background: rgba(0,212,255,.12) !important;
  color: var(--cyan) !important;
  border-radius: 999px !important;
}

/* Slider */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
  background: var(--cyan) !important;
}

/* Checkbox */
[data-testid="stCheckbox"] label span { color: var(--text) !important; }

/* Radio */
[data-testid="stRadio"] label span { color: var(--text) !important; }

/* Plot / Chart background */
.js-plotly-plot { background: transparent !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 5px; }

/* Option menu overrides */
nav-pills .nav-link { color: var(--text-muted) !important; }
nav-pills .nav-link.active { background: var(--cyan) !important; color: #000 !important; }
</style>
"""

SIDEBAR_CSS = """
<style>
.sidebar-logo {
  display: flex; align-items: center; gap: .6rem;
  padding: 1rem 0 1.5rem;
  border-bottom: 1px solid #1E293B;
  margin-bottom: 1rem;
}
.sidebar-logo-icon { font-size: 1.8rem; color: #00D4FF; }
.sidebar-logo-text { font-size: 1.15rem; font-weight: 700; color: #E2E8F0; }
.sidebar-logo-text span { color: #00D4FF; }

.ds-card {
  background: rgba(0,212,255,.06);
  border: 1px solid rgba(0,212,255,.15);
  border-radius: 8px;
  padding: .75rem 1rem;
  margin-bottom: 1.25rem;
}
.ds-card-name { font-size: .82rem; font-weight: 600; color: #E2E8F0; }
.ds-card-stats { font-size: .72rem; color: #00D4FF; margin-top: 2px; }
.ds-card-empty { border-color: #1E293B; background: rgba(255,255,255,.02); }
.ds-card-empty .ds-card-name { color: #94A3B8; }
.ds-card-empty .ds-card-stats { color: #475569; }
</style>
"""


def kpi_row_html(stats: list) -> str:
    cards = ""
    colors = ["#00D4FF", "#7C3AED", "#FF006E", "#10B981", "#F59E0B", "#EF4444"]
    for i, (label, value) in enumerate(stats):
        c = colors[i % len(colors)]
        cards += f"""
        <div style="background:#0D1528;border:1px solid #1E293B;border-radius:10px;
                    padding:1rem 1.4rem;position:relative;overflow:hidden;flex:1;min-width:130px;">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;background:{c};"></div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:1.7rem;font-weight:700;
                      color:{c};">{value}</div>
          <div style="font-size:.72rem;color:#94A3B8;text-transform:uppercase;
                      letter-spacing:.06em;margin-top:.2rem;">{label}</div>
        </div>"""
    return f'<div style="display:flex;gap:.75rem;flex-wrap:wrap;margin:1rem 0;">{cards}</div>'


def section_header(icon: str, title: str, subtitle: str = "") -> str:
    sub = f'<div style="color:#94A3B8;font-size:.9rem;margin-top:.2rem;">{subtitle}</div>' if subtitle else ""
    return f"""
    <div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #1E293B;">
      <div style="display:flex;align-items:center;gap:.6rem;">
        <span style="font-size:1.4rem;">{icon}</span>
        <h2 style="margin:0;font-size:1.4rem;font-weight:700;color:#E2E8F0;">{title}</h2>
      </div>
      {sub}
    </div>"""


def badge(text: str, color: str = "cyan") -> str:
    colors = {
        "cyan": ("rgba(0,212,255,.12)", "#00D4FF"),
        "purple": ("rgba(124,58,237,.12)", "#a78bfa"),
        "pink": ("rgba(255,0,110,.12)", "#fb7185"),
        "green": ("rgba(16,185,129,.12)", "#10B981"),
        "amber": ("rgba(245,158,11,.12)", "#F59E0B"),
        "red": ("rgba(239,68,68,.12)", "#EF4444"),
        "gray": ("rgba(148,163,184,.08)", "#94A3B8"),
    }
    bg, fg = colors.get(color, colors["gray"])
    return f'<span style="background:{bg};color:{fg};padding:.2rem .6rem;border-radius:999px;font-size:.72rem;font-weight:600;font-family:monospace;">{text}</span>'
