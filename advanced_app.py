import streamlit as st
from modules.home import home_page
from modules.upload import upload_page
from modules.profiling import profiling_page
from modules.cleaning import cleaning_page
from modules.eda import eda_page
from modules.visualizations import visualizations_page
from modules.dashboard import dashboard_page
from modules.timeseries import timeseries_page
from modules.export import export_page
from modules.ml_insights import ml_insights_page
from modules.nlq import nlq_page
from modules.live_feed import live_feed_page
from modules.privacy import privacy_page
from modules.terms import terms_page
from modules.cookies import cookies_page

st.set_page_config(
    page_title="DataViz Pro",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600;700;800&display=swap');

/* ═══ RESET & BASE ══════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif !important;
    font-size: 14px;
}

/* ═══ APP BACKGROUND ════════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] {
    background: #060B1A !important;
}
[data-testid="stAppViewContainer"] > .main {
    background: #060B1A !important;
}
[data-testid="stAppViewContainer"] > .main::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}
.main .block-container {
    padding: 1.5rem 2rem 3rem;
    max-width: 1400px;
    position: relative;
    z-index: 1;
}

/* ═══ SIDEBAR ═══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #080D1C !important;
    border-right: 1px solid rgba(0,212,255,0.12) !important;
    min-width: 230px !important;
    max-width: 250px !important;
}
[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00D4FF, transparent);
}

/* ═══ SIDEBAR BUTTONS (nav) ═════════════════════════════════════════════════ */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #8892A4 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: .45rem .9rem !important;
    font-size: .81rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    box-shadow: none !important;
    min-height: unset !important;
    margin: 1px 6px !important;
    width: calc(100% - 12px) !important;
    transform: none !important;
    transition: all .18s ease !important;
    letter-spacing: .01em;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,212,255,0.07) !important;
    color: #00D4FF !important;
    transform: translateX(3px) !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button svg,
[data-testid="stSidebar"] .stButton > button [data-testid="stButtonIcon"] {
    display: none !important;
}

/* ═══ SIDEBAR COLLAPSE BUTTONS ═════════════════════════════════════════════ */
[data-testid="stSidebarCollapseButton"] button span,
[data-testid="stSidebarCollapsedControl"] button span {
    font-size: 0 !important; color: transparent !important; visibility: hidden !important;
}
[data-testid="stSidebarCollapseButton"] button::after {
    content: '‹'; font-size: 1.1rem; color: #8892A4; visibility: visible !important;
}
[data-testid="stSidebarCollapsedControl"] button::after {
    content: '›'; font-size: 1.1rem; color: #8892A4; visibility: visible !important;
}

/* ═══ DIVIDER ════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.06) !important;
    margin: .4rem .6rem !important;
}

/* ═══ PAGE HEADER ═══════════════════════════════════════════════════════════ */
.page-header { margin-bottom: 1.8rem; }
.page-header-eyebrow {
    font-size: .65rem; font-weight: 600; letter-spacing: .15em;
    text-transform: uppercase; color: #00D4FF; margin-bottom: .4rem;
    font-family: 'JetBrains Mono', monospace;
}
.page-header h2 {
    font-size: 1.6rem; font-weight: 700; color: #F0F6FF;
    margin: 0 0 .3rem; line-height: 1.2;
}
.page-header-bar {
    width: 36px; height: 2px; margin: .5rem 0 .6rem;
    background: linear-gradient(90deg, #00D4FF, #7C3AED);
    border-radius: 2px;
}
.page-header p { font-size: .83rem; color: #64748B; margin: 0; }

/* ═══ METRIC CARDS ═══════════════════════════════════════════════════════════ */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.035) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
    backdrop-filter: blur(12px);
    transition: border-color .2s;
}
div[data-testid="stMetric"]:hover {
    border-color: rgba(0,212,255,0.25) !important;
}
div[data-testid="stMetricLabel"] {
    color: #64748B !important; font-size: 0.68rem !important;
    font-weight: 600 !important; text-transform: uppercase;
    letter-spacing: .08em; font-family: 'JetBrains Mono', monospace !important;
}
div[data-testid="stMetricValue"] {
    color: #F0F6FF !important; font-size: 1.55rem !important;
    font-weight: 700 !important; font-family: 'Space Grotesk', sans-serif !important;
}
div[data-testid="stMetricDelta"] { font-size: .78rem !important; }

/* ═══ TABS ════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.06);
    overflow-x: auto;
    flex-wrap: wrap;
}
.stTabs [data-baseweb="tab-list"] > [role="presentation"],
.stTabs button[data-baseweb="tab-bar-scroll-button-left"],
.stTabs button[data-baseweb="tab-bar-scroll-button-right"] {
    display: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px; padding: .38rem .95rem;
    font-size: .78rem; font-weight: 600;
    color: #64748B !important; background: transparent;
    border: none; white-space: nowrap;
    font-family: 'Space Grotesk', sans-serif !important;
    transition: all .15s;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,212,255,0.1) !important;
    color: #00D4FF !important;
    box-shadow: 0 0 0 1px rgba(0,212,255,0.2);
}

/* ═══ BUTTONS ════════════════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #0EA5E9, #7C3AED) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 8px !important;
    padding: .52rem 1.3rem !important; font-weight: 600 !important;
    font-size: .82rem !important; min-height: 40px !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.15) !important;
    transition: all .18s ease !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: .02em !important;
}
.stButton > button:hover {
    box-shadow: 0 0 30px rgba(0,212,255,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ═══ DOWNLOAD BUTTONS ════════════════════════════════════════════════════════ */
.stDownloadButton > button {
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(124,58,237,0.15)) !important;
    color: #00D4FF !important; border: 1px solid rgba(0,212,255,0.3) !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: .82rem !important; min-height: 40px !important;
    transition: all .18s ease !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.25), rgba(124,58,237,0.25)) !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.2) !important;
    transform: translateY(-1px) !important;
}

/* ═══ INPUTS ════════════════════════════════════════════════════════════════ */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; color: #E2E8F0 !important;
    min-height: 40px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(0,212,255,0.5) !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.1) !important;
}
.stSelectbox [data-baseweb="select"] > div:focus-within {
    border-color: rgba(0,212,255,0.5) !important;
}

/* ═══ MULTISELECT ════════════════════════════════════════════════════════════ */
.stMultiSelect [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
}
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(0,212,255,0.15) !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
}

/* ═══ SLIDER ════════════════════════════════════════════════════════════════ */
[data-testid="stSlider"] > div > div > div > div {
    background: linear-gradient(90deg, #00D4FF, #7C3AED) !important;
}

/* ═══ CHECKBOX / RADIO ══════════════════════════════════════════════════════ */
.stCheckbox > label, .stRadio > label {
    color: #A0AEC0 !important; font-size: .83rem !important; font-weight: 500 !important;
}

/* ═══ EXPANDER ══════════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 9px !important; font-weight: 600 !important;
    color: #A0AEC0 !important; padding: .65rem 1rem !important;
}
.streamlit-expanderHeader:hover {
    border-color: rgba(0,212,255,0.2) !important;
    color: #00D4FF !important;
}

/* ═══ DATAFRAME ═════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    overflow: hidden !important;
}

/* ═══ ALERTS / INFO / WARNING ════════════════════════════════════════════════ */
.stAlert {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 10px !important;
    border-left-width: 3px !important;
    font-size: .84rem !important;
}
.stAlert [data-testid="stAlertContentInfo"] {
    color: #00D4FF !important;
}

/* ═══ CODE BLOCK ════════════════════════════════════════════════════════════ */
.stCodeBlock {
    background: rgba(0,0,0,0.4) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}

/* ═══ SPINNER ════════════════════════════════════════════════════════════════ */
.stSpinner > div > div {
    border-top-color: #00D4FF !important;
}

/* ═══ FILE UPLOADER ══════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1.5px dashed rgba(0,212,255,0.25) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(0,212,255,0.5) !important;
    background: rgba(0,212,255,0.03) !important;
}

/* ═══ TOOLTIP / POPOVER ══════════════════════════════════════════════════════ */
[data-testid="stTooltipIcon"] { color: #4A5568 !important; }

/* ═══ SCROLLBAR ══════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.3); }

/* ═══ FOOTER ════════════════════════════════════════════════════════════════ */
.dataviz-footer {
    margin-top: 3rem; padding: 1.5rem 0 .5rem;
    border-top: 1px solid rgba(255,255,255,0.06); text-align: center;
}
.dataviz-footer a {
    color: #00D4FF; text-decoration: none;
    font-size: .78rem; font-weight: 500; margin: 0 .6rem;
    opacity: .7; transition: opacity .15s;
}
.dataviz-footer a:hover { opacity: 1; text-decoration: none; }
.dataviz-footer p { color: #2D3748; font-size: .72rem; margin-top: .5rem; }

/* ═══ MOBILE ════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .main .block-container { padding: .8rem 1rem 2rem !important; }
    .page-header h2 { font-size: 1.25rem !important; }
    div[data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    [data-testid="stSidebar"] { min-width: 210px !important; max-width: 210px !important; }
}

/* ═══ FIX PLOTLY CHART BACKGROUNDS ══════════════════════════════════════════ */
.js-plotly-plot .plotly .bg { fill: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("raw_df", None), ("df", None), ("filename", None), ("_page", "Home")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Navigation definition ──────────────────────────────────────────────────────
_MAIN_PAGES = [
    ("⬡", "Home"),
    ("⬆", "Upload Data"),
    ("◎", "Data Profiling"),
    ("✦", "Data Cleaning"),
    ("∿", "EDA & Statistics"),
    ("▦", "Chart Builder"),
    ("⚡", "Auto Dashboard"),
    ("⏱", "Time Series"),
    ("◈", "ML Insights"),
    ("◐", "Ask Your Data"),
    ("⟳", "Live Data Feed"),
    ("↓", "Export & Reports"),
]
_LEGAL_PAGES = [
    ("⊡", "Privacy Policy"),
    ("⊟", "Terms of Service"),
    ("⊞", "Cookie Policy"),
]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1.2rem 1rem .8rem;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:.5rem;'>
        <div style='display:flex;align-items:center;gap:10px;'>
            <div style='width:36px;height:36px;flex-shrink:0;
                        background:linear-gradient(135deg,#00D4FF22,#7C3AED22);
                        border:1px solid rgba(0,212,255,0.3);
                        border-radius:10px;display:flex;align-items:center;
                        justify-content:center;font-size:1rem;'>⬡</div>
            <div>
                <div style='font-size:.92rem;font-weight:700;color:#F0F6FF;line-height:1.1;
                            font-family:"Space Grotesk",sans-serif;letter-spacing:-.01em;'>DataViz Pro</div>
                <div style='font-size:.6rem;color:#00D4FF;font-weight:500;
                            letter-spacing:.1em;text-transform:uppercase;opacity:.8;
                            font-family:"JetBrains Mono",monospace;'>Advanced Analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for icon, label in _MAIN_PAGES:
        if st.sidebar.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state._page = label
            st.rerun()

    st.divider()
    for icon, label in _LEGAL_PAGES:
        if st.sidebar.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state._page = label
            st.rerun()

    st.divider()
    if st.session_state.df is not None:
        r, c = st.session_state.df.shape
        fn = st.session_state.filename or "dataset"
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(0,212,255,0.07),rgba(124,58,237,0.07));
                    border:1px solid rgba(0,212,255,0.18);border-radius:10px;
                    padding:.8rem 1rem;margin:.2rem .4rem;'>
            <div style='font-size:.57rem;font-weight:600;color:#00D4FF;
                        text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;
                        font-family:"JetBrains Mono",monospace;'>
                Active Dataset
            </div>
            <div style='font-size:.78rem;font-weight:600;color:#F0F6FF;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
                 title='{fn}'>{fn}</div>
            <div style='font-size:.68rem;color:#64748B;margin-top:3px;
                        font-family:"JetBrains Mono",monospace;'>
                {r:,} rows · {c} cols
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:rgba(255,255,255,0.02);border:1.5px dashed rgba(0,212,255,0.15);
                    border-radius:10px;padding:.8rem 1rem;text-align:center;
                    margin:.2rem .4rem;'>
            <div style='font-size:.73rem;color:#4A5568;'>No dataset loaded</div>
            <div style='font-size:.68rem;color:#00D4FF;font-weight:600;margin-top:2px;opacity:.8;'>
                Upload Data to start →
            </div>
        </div>""", unsafe_allow_html=True)

# ── Active page highlight ──────────────────────────────────────────────────────
_active = st.session_state._page
st.markdown(f"""
<script>
(function(){{
  const buttons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
  const target = {repr(_active)};
  buttons.forEach(btn => {{
    btn.style.background = '';
    btn.style.color = '';
    const txt = btn.innerText.trim();
    if (txt.includes(target)) {{
      btn.style.background = 'rgba(0,212,255,0.1)';
      btn.style.color = '#00D4FF';
      btn.style.fontWeight = '700';
      btn.style.borderLeft = '2px solid #00D4FF';
    }}
  }});
}})();
</script>
""", unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
def _footer():
    st.markdown("""
    <div class='dataviz-footer'>
        <p>
            <a href='#' onclick="return false;">Privacy Policy</a>
            &nbsp;·&nbsp;
            <a href='#' onclick="return false;">Terms of Service</a>
            &nbsp;·&nbsp;
            <a href='#' onclick="return false;">Cookie Policy</a>
        </p>
        <p>© 2025 DataViz Pro · All rights reserved</p>
    </div>
    """, unsafe_allow_html=True)


# ── Router ─────────────────────────────────────────────────────────────────────
_ROUTES = {
    "Home":             home_page,
    "Upload Data":      upload_page,
    "Data Profiling":   profiling_page,
    "Data Cleaning":    cleaning_page,
    "EDA & Statistics": eda_page,
    "Chart Builder":    visualizations_page,
    "Auto Dashboard":   dashboard_page,
    "Time Series":      timeseries_page,
    "ML Insights":      ml_insights_page,
    "Ask Your Data":    nlq_page,
    "Live Data Feed":   live_feed_page,
    "Export & Reports": export_page,
    "Privacy Policy":   privacy_page,
    "Terms of Service": terms_page,
    "Cookie Policy":    cookies_page,
}

page = st.session_state._page
if page in _ROUTES:
    _ROUTES[page]()

_footer()
