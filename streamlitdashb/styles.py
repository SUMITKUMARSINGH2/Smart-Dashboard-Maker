DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── RESET & BASE ─────────────────────────────────────────────── */
:root {
  --bg:       #050508;
  --s1:       #0c0c14;
  --s2:       #12121e;
  --s3:       #1a1a2e;
  --border:   rgba(255,255,255,.07);
  --border2:  rgba(255,255,255,.12);
  --text:     #f1f2f6;
  --muted:    #7c7f96;
  --dim:      #3d3f52;
  --sky:      #38bdf8;
  --indigo:   #818cf8;
  --purple:   #a855f7;
  --pink:     #f472b6;
  --green:    #4ade80;
  --amber:    #fbbf24;
  --red:      #f87171;
}

html, body, [class*="css"] {
  font-family: 'Inter', system-ui, sans-serif !important;
  -webkit-font-smoothing: antialiased !important;
}

/* App background with subtle mesh */
.stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
}
.stApp::before {
  content: '';
  position: fixed;
  top: -200px; left: -200px;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(99,102,241,.08) 0%, transparent 70%);
  pointer-events: none; z-index: 0;
}
.stApp::after {
  content: '';
  position: fixed;
  bottom: -200px; right: -200px;
  width: 700px; height: 700px;
  background: radial-gradient(circle, rgba(168,85,247,.06) 0%, transparent 70%);
  pointer-events: none; z-index: 0;
}

/* ── HIDE STREAMLIT CHROME ─────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { visibility: hidden !important; }
.viewerBadge_container__r5tak { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── TYPOGRAPHY ────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 { color: var(--text) !important; font-weight: 700 !important; }
p, span, label, div { color: var(--text) !important; }
a { color: var(--sky) !important; }

/* ── RAINBOW GRADIENT TEXT ─────────────────────────────────────── */
@keyframes rainbowFlow {
  0%   { background-position: 0% center; }
  100% { background-position: 200% center; }
}

/* ── SIDEBAR ───────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: var(--s1) !important;
  border-right: 1px solid var(--border) !important;
  padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] small { color: var(--muted) !important; }

/* ── BUTTONS ────────────────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: .9rem !important;
  padding: .6rem 1.5rem !important;
  transition: all .2s ease !important;
  box-shadow: 0 4px 15px rgba(139,92,246,.25) !important;
  letter-spacing: .01em !important;
}
.stButton > button:hover {
  transform: translateY(-2px) scale(1.01) !important;
  box-shadow: 0 8px 30px rgba(139,92,246,.45) !important;
  opacity: 1 !important;
}
.stButton > button:active { transform: translateY(0) !important; }

.stDownloadButton > button {
  background: rgba(56,189,248,.08) !important;
  color: var(--sky) !important;
  border: 1px solid rgba(56,189,248,.25) !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  box-shadow: none !important;
}

/* ── INPUTS ─────────────────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  background: var(--s2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--indigo) !important;
  box-shadow: 0 0 0 3px rgba(129,140,248,.15) !important;
}

/* ── SELECT ─────────────────────────────────────────────────────── */
[data-baseweb="select"] { background: var(--s2) !important; border-radius: 10px !important; }
[data-baseweb="select"] > div {
  background: var(--s2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}
[data-baseweb="select"] input { background: transparent !important; color: var(--text) !important; }
[data-baseweb="select"] span { color: var(--text) !important; }
[data-baseweb="select"] svg { fill: var(--muted) !important; }
[data-baseweb="popover"] {
  background: var(--s1) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 12px !important;
  box-shadow: 0 16px 48px rgba(0,0,0,.6) !important;
}
[data-baseweb="menu"] { background: var(--s1) !important; }
[data-baseweb="menu"] ul { background: transparent !important; padding: 6px !important; }
li[role="option"] {
  background: transparent !important;
  color: var(--text) !important;
  border-radius: 8px !important;
  font-size: .88rem !important;
}
li[role="option"]:hover { background: var(--s2) !important; }
li[role="option"][aria-selected="true"] {
  background: rgba(129,140,248,.12) !important;
  color: var(--indigo) !important;
}

/* ── NUMBER INPUT ─────────────────────────────────────────────── */
[data-baseweb="input"] {
  background: var(--s2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
}
[data-testid="stNumberInput"] input { background: transparent !important; color: var(--text) !important; }
[data-testid="stNumberInput"] button {
  background: var(--s3) !important;
  color: var(--muted) !important;
  border: none !important;
}

/* ── FILE UPLOADER ───────────────────────────────────────────── */
[data-testid="stFileUploader"] { background: transparent !important; border: none !important; }
[data-testid="stFileUploaderDropzone"] {
  background: var(--s2) !important;
  border: 2px dashed rgba(129,140,248,.3) !important;
  border-radius: 16px !important;
  transition: all .2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: var(--indigo) !important;
  background: rgba(129,140,248,.05) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { color: var(--muted) !important; }
[data-testid="stFileUploaderDropzoneInstructions"] span { color: var(--muted) !important; }
[data-testid="stFileUploaderDropzoneInstructions"] svg { fill: var(--dim) !important; }
[data-testid="stFileUploader"] button {
  background: rgba(129,140,248,.1) !important;
  color: var(--indigo) !important;
  border: 1px solid rgba(129,140,248,.3) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
}
[data-testid="stFileUploader"] small { color: var(--dim) !important; }

/* ── METRICS ─────────────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--s2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 1.1rem 1.3rem !important;
}
[data-testid="stMetric"] label { color: var(--muted) !important; font-size: .72rem !important; text-transform: uppercase !important; letter-spacing: .08em !important; }
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; font-size: 1.7rem !important; font-weight: 700 !important; color: var(--text) !important; }

/* ── TABS ────────────────────────────────────────────────────── */
[data-testid="stTabs"] {
  border-bottom: 1px solid var(--border) !important;
}
[data-testid="stTabs"] button {
  background: transparent !important;
  color: var(--muted) !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  font-weight: 600 !important;
  font-size: .88rem !important;
  transition: all .15s !important;
}
[data-testid="stTabs"] button:hover { color: var(--text) !important; }
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--indigo) !important;
  border-bottom-color: var(--indigo) !important;
}

/* ── DATAFRAME ───────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
}

/* ── ALERTS ──────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; border-left: 3px solid !important; }
[data-testid="stAlert"][data-baseweb="notification"] { background: var(--s2) !important; }

/* ── EXPANDER ────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--s2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; font-weight: 600 !important; }

/* ── MULTISELECT ─────────────────────────────────────────────── */
[data-baseweb="tag"] {
  background: rgba(129,140,248,.15) !important;
  color: var(--indigo) !important;
  border-radius: 999px !important;
}

/* ── SLIDER ──────────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] div { background: var(--s3) !important; }
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
  background: var(--indigo) !important;
  border-color: var(--indigo) !important;
}

/* ── CHECKBOX / RADIO ─────────────────────────────────────────── */
[data-testid="stCheckbox"] label span,
[data-testid="stRadio"] label span { color: var(--text) !important; }

/* ── TOOLTIP ─────────────────────────────────────────────────── */
[data-baseweb="tooltip"] div {
  background: var(--s1) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text) !important;
  border-radius: 8px !important;
}

/* ── SCROLLBAR ───────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--s3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--indigo); }

/* ── PLOTLY ──────────────────────────────────────────────────── */
.js-plotly-plot { background: transparent !important; }

/* ── OPTION MENU OVERRIDE ────────────────────────────────────── */
nav.nav { background: transparent !important; }
.nav-pills .nav-link {
  color: var(--muted) !important;
  border-radius: 8px !important;
  font-size: .85rem !important;
  font-weight: 500 !important;
  padding: .45rem .75rem !important;
  transition: all .15s !important;
  margin-bottom: 2px !important;
}
.nav-pills .nav-link:hover { background: var(--s2) !important; color: var(--text) !important; }
.nav-pills .nav-link.active {
  background: linear-gradient(135deg, rgba(99,102,241,.2), rgba(168,85,247,.2)) !important;
  color: var(--indigo) !important;
  font-weight: 600 !important;
  box-shadow: inset 3px 0 0 var(--indigo) !important;
}
.nav-pills .nav-link.active i { color: var(--indigo) !important; }
nav.nav i { font-size: .9rem !important; }
</style>
"""

SIDEBAR_CSS = """
<style>
@keyframes rainbowFlow {
  0%   { background-position: 0% center; }
  100% { background-position: 200% center; }
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: .6; }
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: .6rem;
  padding: 1.5rem 1rem 1.2rem;
  border-bottom: 1px solid rgba(255,255,255,.06);
  margin-bottom: 1rem;
  background: linear-gradient(180deg, rgba(99,102,241,.05) 0%, transparent 100%);
}
.sidebar-logo-icon {
  font-size: 1.8rem;
  background: linear-gradient(90deg,#ff0000,#ff7700,#ffee00,#00ff88,#00cfff,#7700ff,#ff00cc,#ff0000);
  background-size: 300% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: rainbowFlow 2s linear infinite;
  filter: drop-shadow(0 0 8px rgba(99,102,241,.5));
}
.sidebar-logo-text {
  font-size: 1.1rem;
  font-weight: 800;
  color: #f1f2f6;
  letter-spacing: -.5px;
  line-height: 1;
}
.sidebar-logo-sub {
  font-size: .65rem;
  color: #7c7f96;
  font-weight: 400;
  letter-spacing: .04em;
  text-transform: uppercase;
  margin-top: 2px;
}

.ds-card {
  background: linear-gradient(135deg, rgba(99,102,241,.08), rgba(168,85,247,.05));
  border: 1px solid rgba(129,140,248,.2);
  border-radius: 12px;
  padding: .75rem 1rem;
  margin-bottom: 1rem;
  position: relative;
  overflow: hidden;
}
.ds-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, #6366f1, #a855f7);
}
.ds-card-name { font-size: .8rem; font-weight: 700; color: #f1f2f6; }
.ds-card-stats { font-size: .7rem; color: #818cf8; margin-top: 3px; }
.ds-card-empty {
  background: rgba(255,255,255,.02);
  border: 1px solid rgba(255,255,255,.05);
}
.ds-card-empty::before { background: rgba(255,255,255,.04); }
.ds-card-empty .ds-card-name { color: #3d3f52; }
.ds-card-empty .ds-card-stats { color: #2d2f42; }
</style>
"""


def kpi_row_html(stats: list) -> str:
    colors = [
        ("#818cf8", "rgba(129,140,248,.08)"),
        ("#f472b6", "rgba(244,114,182,.08)"),
        ("#4ade80", "rgba(74,222,128,.08)"),
        ("#fbbf24", "rgba(251,191,36,.08)"),
        ("#38bdf8", "rgba(56,189,248,.08)"),
        ("#a855f7", "rgba(168,85,247,.08)"),
    ]
    cards = ""
    for i, (label, value) in enumerate(stats):
        fg, bg = colors[i % len(colors)]
        cards += f"""
        <div style="background:{bg};border:1px solid rgba(255,255,255,.06);
                    border-radius:14px;padding:1rem 1.2rem;flex:1;min-width:110px;
                    position:relative;overflow:hidden;">
          <div style="position:absolute;top:0;left:0;right:0;height:2px;background:{fg};opacity:.6;"></div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:1.55rem;
                      font-weight:700;color:{fg};line-height:1;">{value}</div>
          <div style="font-size:.65rem;color:#7c7f96;text-transform:uppercase;
                      letter-spacing:.1em;margin-top:.35rem;">{label}</div>
        </div>"""
    return f'<div style="display:flex;gap:.6rem;flex-wrap:wrap;margin:.75rem 0;">{cards}</div>'


def section_header(icon: str, title: str, subtitle: str = "") -> str:
    sub = f'<div style="color:#7c7f96;font-size:.84rem;margin-top:.2rem;">{subtitle}</div>' if subtitle else ""
    return f"""
    <div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid rgba(255,255,255,.06);">
      <div style="display:flex;align-items:center;gap:.55rem;">
        <span style="font-size:1.25rem;">{icon}</span>
        <h2 style="margin:0;font-size:1.3rem;font-weight:700;color:#f1f2f6;">{title}</h2>
      </div>
      {sub}
    </div>"""


def badge(text: str, color: str = "indigo") -> str:
    palette = {
        "indigo": ("rgba(129,140,248,.15)", "#818cf8"),
        "sky":    ("rgba(56,189,248,.12)",  "#38bdf8"),
        "pink":   ("rgba(244,114,182,.12)", "#f472b6"),
        "green":  ("rgba(74,222,128,.12)",  "#4ade80"),
        "amber":  ("rgba(251,191,36,.12)",  "#fbbf24"),
        "red":    ("rgba(248,113,113,.12)", "#f87171"),
        "purple": ("rgba(168,85,247,.12)",  "#a855f7"),
        "gray":   ("rgba(124,127,150,.10)", "#7c7f96"),
    }
    bg, fg = palette.get(color, palette["gray"])
    return f'<span style="background:{bg};color:{fg};padding:.2rem .65rem;border-radius:999px;font-size:.7rem;font-weight:600;letter-spacing:.02em;">{text}</span>'
