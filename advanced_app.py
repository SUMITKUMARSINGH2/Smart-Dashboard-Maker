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
from modules.privacy import privacy_page
from modules.terms import terms_page
from modules.cookies import cookies_page

st.set_page_config(
    page_title="DataViz Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ═══ GLOBAL ═══════════════════════════════════════════════════════════════ */
*, html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* ═══ APP SHELL ════════════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] > .main { background: #F8FAFC; }
.main .block-container { padding: 1.5rem 2rem 3rem; max-width: 1400px; }

/* ═══ SIDEBAR ══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    min-width: 230px !important;
    max-width: 250px !important;
}
/* Hide the default Streamlit radio dot */
[data-testid="stSidebar"] .stRadio > div { gap: 0 !important; }
[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] { display: none; }
[data-testid="stSidebar"] .stRadio > div > label {
    display: flex;
    align-items: center;
    padding: .42rem .9rem !important;
    border-radius: 8px !important;
    margin: 1px 4px !important;
    cursor: pointer;
    transition: background .12s;
    font-size: .82rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
    white-space: nowrap;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: #F5F3FF !important;
    color: #7C3AED !important;
}
[data-testid="stSidebar"] .stRadio > div > label[data-baseweb] { background: transparent; }

/* Hide the actual radio circle */
[data-testid="stSidebar"] .stRadio > div > label > div:first-child { display: none !important; }

/* Selected state — Streamlit adds aria-checked to the label's inner span */
[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
    background: linear-gradient(135deg, #EDE9FE, #FCE7F3) !important;
    color: #7C3AED !important;
    font-weight: 800 !important;
}

/* ═══ PAGE HEADER ══════════════════════════════════════════════════════════ */
.page-header { margin-bottom: 1.5rem; padding-bottom: .3rem; }
.page-header h2 { font-size: 1.5rem; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-header::after {
    content: ''; display: block; width: 40px; height: 4px;
    background: linear-gradient(90deg, #7C3AED, #F43F5E);
    border-radius: 2px; margin: 8px 0;
}
.page-header p { font-size: .85rem; color: #6B7280; margin: 0; }

/* ═══ METRIC CARDS ══════════════════════════════════════════════════════════ */
div[data-testid="stMetric"] {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 12px; padding: 1rem 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
div[data-testid="stMetricLabel"] {
    color: #6B7280 !important; font-size: 0.72rem !important;
    font-weight: 600 !important; text-transform: uppercase; letter-spacing: .05em;
}
div[data-testid="stMetricValue"] {
    color: #0F172A !important; font-size: 1.5rem !important; font-weight: 800 !important;
}

/* ═══ TABS — hide scroll arrows, wrap labels ════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #F1F5F9;
    border-radius: 10px;
    padding: 4px;
    border: none;
    overflow-x: auto;
    flex-wrap: wrap;
}
/* Hide the ◀ ▶ scroll arrow buttons Streamlit injects */
.stTabs [data-baseweb="tab-list"] > [role="presentation"],
.stTabs [data-baseweb="tab-list"] button[aria-label="Scroll left"],
.stTabs [data-baseweb="tab-list"] button[aria-label="Scroll right"],
.stTabs button[data-baseweb="tab-bar-scroll-button-left"],
.stTabs button[data-baseweb="tab-bar-scroll-button-right"],
[data-testid="stTabs"] > div > div:first-child > div:first-child:not([role="tab"]):not([role="tablist"]),
[data-testid="stTabs"] > div > div:first-child button:not([role="tab"]) {
    display: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    padding: 0.38rem .9rem;
    font-size: 0.8rem;
    font-weight: 600;
    color: #6B7280 !important;
    background: transparent;
    border: none;
    white-space: nowrap;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #7C3AED !important;
    box-shadow: 0 1px 4px rgba(124,58,237,.15);
}

/* ═══ BUTTONS ════════════════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #7C3AED, #9333EA);
    color: white !important; border: none; border-radius: 9px;
    padding: .55rem 1.3rem; font-weight: 700; font-size: .84rem;
    min-height: 44px; box-shadow: 0 2px 8px rgba(124,58,237,.28);
    transition: all .15s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6D28D9, #7C3AED);
    box-shadow: 0 4px 14px rgba(124,58,237,.4);
    transform: translateY(-1px); color: white !important;
}
.stButton > button[kind="secondary"] {
    background: #FFFFFF; color: #7C3AED !important;
    border: 1.5px solid #DDD6FE; box-shadow: none;
}

/* ═══ DOWNLOAD BUTTONS ══════════════════════════════════════════════════════ */
.stDownloadButton > button {
    background: linear-gradient(135deg, #F43F5E, #E11D48);
    color: white !important; border: none; border-radius: 9px;
    font-weight: 700; padding: .55rem 1.3rem; min-height: 44px;
    box-shadow: 0 2px 8px rgba(244,63,94,.28);
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #E11D48, #BE123C);
    box-shadow: 0 4px 14px rgba(244,63,94,.4);
    transform: translateY(-1px); color: white !important;
}

/* ═══ INPUTS ═════════════════════════════════════════════════════════════════ */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput > div > div > input {
    background: #FFFFFF; border: 1.5px solid #E2E8F0;
    border-radius: 8px; color: #0F172A; min-height: 42px;
}
.stTextInput > div > div > input:focus { border-color: #7C3AED; }
.stSelectbox [data-baseweb="select"] > div:focus-within { border-color: #7C3AED !important; }

/* ═══ ALERTS ═════════════════════════════════════════════════════════════════ */
.stAlert { border-radius: 10px; font-size: .875rem; }

/* ═══ EXPANDER ══════════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: #FFFFFF; border: 1.5px solid #E2E8F0;
    border-radius: 9px; font-weight: 700; color: #0F172A; padding: .7rem 1rem;
}

/* ═══ DATAFRAME ══════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #E2E8F0; }

/* ═══ RADIO / CHECKBOX ════════════════════════════════════════════════════════ */
.stRadio > label { font-weight: 600; color: #374151; font-size: .83rem; }

/* ═══ SLIDER ════════════════════════════════════════════════════════════════ */
[data-testid="stSlider"] > div > div > div > div { background: #7C3AED !important; }

/* ═══ FOOTER ════════════════════════════════════════════════════════════════ */
.dataviz-footer {
    margin-top: 3rem; padding: 1.5rem 0 .5rem;
    border-top: 1px solid #E2E8F0; text-align: center;
}
.dataviz-footer a {
    color: #7C3AED; text-decoration: none;
    font-size: .8rem; font-weight: 500; margin: 0 .6rem;
}
.dataviz-footer a:hover { text-decoration: underline; }
.dataviz-footer p { color: #94A3B8; font-size: .75rem; margin-top: .5rem; }

/* ═══ MOBILE ════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .main .block-container { padding: .8rem 1rem 2rem !important; }
    .page-header h2 { font-size: 1.25rem !important; }
    div[data-testid="stMetricValue"] { font-size: 1.25rem !important; }
    [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
    .stTabs [data-baseweb="tab"] { padding: .32rem .6rem !important; font-size: .74rem !important; }
    .stButton > button, .stDownloadButton > button {
        min-height: 48px !important; font-size: .85rem !important; width: 100% !important;
    }
    .stSelectbox [data-baseweb="select"] > div,
    .stTextInput > div > div > input { min-height: 48px !important; font-size: .9rem !important; }
    [data-testid="stSidebar"] { min-width: 210px !important; max-width: 210px !important; }
}
@media (max-width: 480px) {
    .main .block-container { padding: .6rem .7rem 2rem !important; }
    .page-header h2 { font-size: 1.1rem !important; }
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("raw_df", None), ("df", None), ("filename", None), ("_page", "Home")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Navigation definition ──────────────────────────────────────────────────────
_MAIN_PAGES = [
    ("🏠", "Home"),
    ("📂", "Upload Data"),
    ("🔍", "Data Profiling"),
    ("✨", "Data Cleaning"),
    ("📈", "EDA & Statistics"),
    ("📊", "Chart Builder"),
    ("⚡", "Auto Dashboard"),
    ("📅", "Time Series"),
    ("🤖", "ML Insights"),
    ("💬", "Ask Your Data"),
    ("📤", "Export & Reports"),
]
_LEGAL_PAGES = [
    ("🔒", "Privacy Policy"),
    ("📄", "Terms of Service"),
    ("🍪", "Cookie Policy"),
]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo + brand
    st.markdown("""
    <div style='padding:.9rem 1rem .6rem;border-bottom:1px solid #F1F5F9;margin-bottom:.4rem;'>
        <div style='display:flex;align-items:center;gap:10px;'>
            <div style='width:34px;height:34px;flex-shrink:0;
                        background:linear-gradient(135deg,#7C3AED,#F43F5E);
                        border-radius:9px;display:flex;align-items:center;
                        justify-content:center;font-size:.95rem;'>📊</div>
            <div>
                <div style='font-size:.9rem;font-weight:800;color:#0F172A;line-height:1.1;'>DataViz Pro</div>
                <div style='font-size:.63rem;color:#9CA3AF;font-weight:500;'>Advanced Analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main nav
    for icon, label in _MAIN_PAGES:
        if st.sidebar.button(f"{icon}  {label}", key=f"nav_{label}",
                              use_container_width=True):
            st.session_state._page = label
            st.rerun()

    # Separator + legal
    st.divider()
    for icon, label in _LEGAL_PAGES:
        active = st.session_state._page == label
        if st.sidebar.button(f"{icon}  {label}", key=f"nav_{label}",
                              use_container_width=True):
            st.session_state._page = label
            st.rerun()

    # Dataset info badge
    st.divider()
    if st.session_state.df is not None:
        r, c = st.session_state.df.shape
        fn = st.session_state.filename or "dataset"
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#F5F3FF,#FDF2F8);
                    border:1.5px solid #DDD6FE;border-radius:10px;
                    padding:.75rem 1rem;margin:.3rem .4rem;'>
            <div style='font-size:.58rem;font-weight:800;color:#7C3AED;
                        text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px;'>
                Active Dataset
            </div>
            <div style='font-size:.78rem;font-weight:700;color:#0F172A;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
                 title='{fn}'>{fn}</div>
            <div style='font-size:.7rem;color:#9CA3AF;margin-top:2px;'>
                {r:,} rows · {c} cols
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#F9FAFB;border:1.5px dashed #DDD6FE;
                    border-radius:10px;padding:.75rem 1rem;text-align:center;
                    margin:.3rem .4rem;'>
            <div style='font-size:.75rem;color:#9CA3AF;'>No dataset loaded</div>
            <div style='font-size:.7rem;color:#7C3AED;font-weight:700;margin-top:2px;'>
                Upload Data to start →
            </div>
        </div>""", unsafe_allow_html=True)

# ── CSS override: style the sidebar buttons to look like nav items ─────────────
st.markdown("""
<style>
/* Make sidebar buttons look like nav links, not buttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #374151 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: .42rem .9rem !important;
    font-size: .82rem !important;
    font-weight: 600 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    box-shadow: none !important;
    min-height: unset !important;
    margin: 1px 4px !important;
    width: calc(100% - 8px) !important;
    transform: none !important;
    transition: background .12s, color .12s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #F5F3FF !important;
    color: #7C3AED !important;
    transform: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# Apply active page highlight via JS (targets the correct button by text content)
_active = st.session_state._page
st.markdown(f"""
<script>
(function(){{
  const buttons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
  const target = {repr(_active)};
  buttons.forEach(btn => {{
    const txt = btn.innerText.trim();
    if (txt.includes(target)) {{
      btn.style.background = 'linear-gradient(135deg,#EDE9FE,#FCE7F3)';
      btn.style.color = '#7C3AED';
      btn.style.fontWeight = '800';
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
    "Export & Reports": export_page,
    "Privacy Policy":   privacy_page,
    "Terms of Service": terms_page,
    "Cookie Policy":    cookies_page,
}

page = st.session_state._page
if page in _ROUTES:
    _ROUTES[page]()

_footer()
