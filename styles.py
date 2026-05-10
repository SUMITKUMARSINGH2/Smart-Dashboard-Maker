DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #0a0a0f;
  --surface: #12121a;
  --surface2: #1a1a26;
  --border: #2a2a3d;
  --text: #f0f0ff;
  --muted: #8888aa;
}

html, body, [class*="css"] {
  font-family: 'Poppins', system-ui, sans-serif !important;
}

.stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* Rainbow animated title */
@keyframes rainbow {
  0%   { color: #ff0000; text-shadow: 0 0 20px #ff0000, 0 0 40px #ff000066; }
  10%  { color: #ff6600; text-shadow: 0 0 20px #ff6600, 0 0 40px #ff660066; }
  20%  { color: #ffcc00; text-shadow: 0 0 20px #ffcc00, 0 0 40px #ffcc0066; }
  30%  { color: #33ff00; text-shadow: 0 0 20px #33ff00, 0 0 40px #33ff0066; }
  40%  { color: #00ffcc; text-shadow: 0 0 20px #00ffcc, 0 0 40px #00ffcc66; }
  50%  { color: #0099ff; text-shadow: 0 0 20px #0099ff, 0 0 40px #0099ff66; }
  60%  { color: #6600ff; text-shadow: 0 0 20px #6600ff, 0 0 40px #6600ff66; }
  70%  { color: #cc00ff; text-shadow: 0 0 20px #cc00ff, 0 0 40px #cc00ff66; }
  80%  { color: #ff0099; text-shadow: 0 0 20px #ff0099, 0 0 40px #ff009966; }
  90%  { color: #ff3333; text-shadow: 0 0 20px #ff3333, 0 0 40px #ff333366; }
  100% { color: #ff0000; text-shadow: 0 0 20px #ff0000, 0 0 40px #ff000066; }
}

@keyframes bgPulse {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes floatUp {
  0%   { transform: translateY(0px); }
  50%  { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

@keyframes shimmer {
  0%   { opacity: 0.6; }
  50%  { opacity: 1; }
  100% { opacity: 0.6; }
}

@keyframes borderRainbow {
  0%   { border-color: #ff0000; box-shadow: 0 0 15px #ff000044; }
  16%  { border-color: #ff9900; box-shadow: 0 0 15px #ff990044; }
  33%  { border-color: #ffff00; box-shadow: 0 0 15px #ffff0044; }
  50%  { border-color: #00ff99; box-shadow: 0 0 15px #00ff9944; }
  66%  { border-color: #0099ff; box-shadow: 0 0 15px #0099ff44; }
  83%  { border-color: #cc00ff; box-shadow: 0 0 15px #cc00ff44; }
  100% { border-color: #ff0000; box-shadow: 0 0 15px #ff000044; }
}

.rainbow-title {
  animation: rainbow 1s linear infinite;
  font-weight: 900 !important;
  font-size: clamp(2.5rem, 6vw, 4rem) !important;
  letter-spacing: -1px;
}

.rainbow-border {
  animation: borderRainbow 1s linear infinite;
  border: 2px solid;
  border-radius: 16px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #12121a 0%, #0f0f1a 100%) !important;
  border-right: 1px solid #2a2a3d !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] p { color: var(--muted) !important; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { visibility: hidden !important; }

/* Headings */
h1 { color: var(--text) !important; font-weight: 800 !important; }
h2, h3, h4, h5, h6 { color: var(--text) !important; font-weight: 700 !important; }
p, span, label { color: var(--text) !important; }

/* Metric cards */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 1.2rem 1.5rem !important;
}
[data-testid="stMetric"] label {
  color: var(--muted) !important;
  font-size: .75rem !important;
  text-transform: uppercase !important;
  letter-spacing: .08em !important;
}
[data-testid="stMetricValue"] {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 1.8rem !important;
  font-weight: 700 !important;
}

/* Tabs */
[data-testid="stTabs"] button {
  background: transparent !important;
  color: var(--muted) !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  font-weight: 600 !important;
  transition: all .2s !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: #a855f7 !important;
  border-bottom-color: #a855f7 !important;
  background: transparent !important;
}

/* Buttons */
.stButton > button {
  background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Poppins', sans-serif !important;
  font-weight: 700 !important;
  padding: .6rem 1.5rem !important;
  transition: all .25s !important;
  letter-spacing: .02em !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(168,85,247,.4) !important;
}
.stDownloadButton > button {
  background: rgba(168,85,247,.1) !important;
  color: #a855f7 !important;
  border: 1px solid rgba(168,85,247,.35) !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea,
[data-baseweb="select"] div, [data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Poppins', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: #a855f7 !important;
  box-shadow: 0 0 0 3px rgba(168,85,247,.15) !important;
}
[data-baseweb="select"] { background: var(--surface2) !important; }

/* File uploader */
[data-testid="stFileUploader"] {
  background: rgba(168,85,247,.04) !important;
  border: 2px dashed rgba(168,85,247,.3) !important;
  border-radius: 14px !important;
  padding: 2rem !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: #a855f7 !important;
  background: rgba(168,85,247,.08) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
}

/* Alerts */
[data-testid="stAlert"] {
  border-radius: 10px !important;
  border-left: 4px solid !important;
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
  background: rgba(168,85,247,.15) !important;
  color: #a855f7 !important;
  border-radius: 999px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2a3d; border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: #a855f7; }

/* Plot */
.js-plotly-plot { background: transparent !important; }
</style>
"""

SIDEBAR_CSS = """
<style>
.sidebar-logo {
  display: flex; align-items: center; gap: .6rem;
  padding: 1rem 0 1.5rem;
  border-bottom: 1px solid #2a2a3d;
  margin-bottom: 1rem;
}
.sidebar-logo-icon {
  font-size: 1.8rem;
  animation: rainbow 1s linear infinite;
}
@keyframes rainbow {
  0%   { color: #ff0000; }
  16%  { color: #ff9900; }
  33%  { color: #ffff00; }
  50%  { color: #00ff99; }
  66%  { color: #0099ff; }
  83%  { color: #cc00ff; }
  100% { color: #ff0000; }
}
.sidebar-logo-text { font-size: 1.15rem; font-weight: 800; color: #f0f0ff; letter-spacing: -.5px; }
.sidebar-logo-text span { color: #a855f7; }

.ds-card {
  background: rgba(168,85,247,.07);
  border: 1px solid rgba(168,85,247,.2);
  border-radius: 10px;
  padding: .75rem 1rem;
  margin-bottom: 1.25rem;
}
.ds-card-name { font-size: .82rem; font-weight: 700; color: #f0f0ff; }
.ds-card-stats { font-size: .72rem; color: #a855f7; margin-top: 3px; }
.ds-card-empty { border-color: #2a2a3d; background: rgba(255,255,255,.02); }
.ds-card-empty .ds-card-name { color: #8888aa; }
.ds-card-empty .ds-card-stats { color: #55557a; }
</style>
"""


def kpi_row_html(stats: list) -> str:
    colors = ["#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff", "#c77dff", "#ff9f1c"]
    cards = ""
    for i, (label, value) in enumerate(stats):
        c = colors[i % len(colors)]
        cards += f"""
        <div style="background:#12121a;border:1px solid #2a2a3d;border-radius:14px;
                    padding:1.1rem 1.4rem;position:relative;overflow:hidden;flex:1;min-width:120px;">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;
                      background:linear-gradient(90deg,{c},{c}88);"></div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:1.7rem;font-weight:700;
                      color:{c};">{value}</div>
          <div style="font-size:.7rem;color:#8888aa;text-transform:uppercase;
                      letter-spacing:.08em;margin-top:.2rem;">{label}</div>
        </div>"""
    return f'<div style="display:flex;gap:.75rem;flex-wrap:wrap;margin:1rem 0;">{cards}</div>'


def section_header(icon: str, title: str, subtitle: str = "") -> str:
    sub = f'<div style="color:#8888aa;font-size:.88rem;margin-top:.2rem;">{subtitle}</div>' if subtitle else ""
    return f"""
    <div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #2a2a3d;">
      <div style="display:flex;align-items:center;gap:.6rem;">
        <span style="font-size:1.4rem;">{icon}</span>
        <h2 style="margin:0;font-size:1.4rem;font-weight:700;color:#f0f0ff;">{title}</h2>
      </div>
      {sub}
    </div>"""


def badge(text: str, color: str = "purple") -> str:
    colors = {
        "purple": ("rgba(168,85,247,.15)", "#a855f7"),
        "cyan":   ("rgba(0,212,255,.12)", "#00D4FF"),
        "pink":   ("rgba(255,0,110,.12)", "#fb7185"),
        "green":  ("rgba(16,185,129,.12)", "#10B981"),
        "amber":  ("rgba(245,158,11,.12)", "#F59E0B"),
        "red":    ("rgba(239,68,68,.12)", "#EF4444"),
        "gray":   ("rgba(148,163,184,.08)", "#8888aa"),
    }
    bg, fg = colors.get(color, colors["gray"])
    return f'<span style="background:{bg};color:{fg};padding:.2rem .6rem;border-radius:999px;font-size:.72rem;font-weight:600;font-family:monospace;">{text}</span>'
