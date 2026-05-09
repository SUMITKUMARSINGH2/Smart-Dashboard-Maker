import streamlit as st
from streamlit_option_menu import option_menu
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

/* ═══ GLOBAL ══════════════════════════════════════════════════════════════ */
*, html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* ═══ APP SHELL ════════════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] > .main {
    background: #F8FAFC;
}
.main .block-container {
    padding: 1.5rem 2rem 3rem;
    max-width: 1400px;
}

/* ═══ SIDEBAR ══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    min-width: 240px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] * { color: #374151 !important; }
[data-testid="stSidebarNavItems"] { padding-top: 0 !important; }

/* ═══ PAGE HEADER ══════════════════════════════════════════════════════════ */
.page-header { margin-bottom: 1.5rem; padding-bottom: .3rem; }
.page-header h2 {
    font-size: 1.5rem; font-weight: 800; color: #0F172A; margin: 0 0 4px;
}
.page-header::after {
    content: ''; display: block; width: 40px; height: 4px;
    background: linear-gradient(90deg, #7C3AED, #F43F5E);
    border-radius: 2px; margin: 8px 0;
}
.page-header p { font-size: .85rem; color: #6B7280; margin: 0; }

/* ═══ METRIC CARDS ══════════════════════════════════════════════════════════ */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
div[data-testid="stMetricLabel"] {
    color: #6B7280 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: .05em;
}
div[data-testid="stMetricValue"] {
    color: #0F172A !important;
    font-size: 1.5rem !important;
    font-weight: 800 !important;
}

/* ═══ TABS ══════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #F1F5F9;
    border-radius: 10px;
    padding: 4px;
    border: none;
    flex-wrap: wrap;
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
    color: white !important;
    border: none;
    border-radius: 9px;
    padding: .55rem 1.3rem;
    font-weight: 700;
    font-size: .84rem;
    min-height: 44px;
    box-shadow: 0 2px 8px rgba(124,58,237,.28);
    transition: all .15s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6D28D9, #7C3AED);
    box-shadow: 0 4px 14px rgba(124,58,237,.4);
    transform: translateY(-1px);
    color: white !important;
}
.stButton > button[kind="secondary"] {
    background: #FFFFFF;
    color: #7C3AED !important;
    border: 1.5px solid #DDD6FE;
    box-shadow: none;
}

/* ═══ DOWNLOAD BUTTONS ════════════════════════════════════════════════════════ */
.stDownloadButton > button {
    background: linear-gradient(135deg, #F43F5E, #E11D48);
    color: white !important;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    padding: .55rem 1.3rem;
    min-height: 44px;
    box-shadow: 0 2px 8px rgba(244,63,94,.28);
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #E11D48, #BE123C);
    box-shadow: 0 4px 14px rgba(244,63,94,.4);
    transform: translateY(-1px);
    color: white !important;
}

/* ═══ INPUTS ══════════════════════════════════════════════════════════════════ */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput > div > div > input {
    background: #FFFFFF;
    border: 1.5px solid #E2E8F0;
    border-radius: 8px;
    color: #0F172A;
    min-height: 42px;
}
.stTextInput > div > div > input:focus { border-color: #7C3AED; }
.stSelectbox [data-baseweb="select"] > div:focus-within { border-color: #7C3AED !important; }

/* ═══ ALERTS ══════════════════════════════════════════════════════════════════ */
.stAlert { border-radius: 10px; font-size: .875rem; }

/* ═══ EXPANDER ═══════════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: #FFFFFF;
    border: 1.5px solid #E2E8F0;
    border-radius: 9px;
    font-weight: 700;
    color: #0F172A;
    padding: .7rem 1rem;
}

/* ═══ DATAFRAME ═══════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
}

/* ═══ RADIO / CHECKBOX ════════════════════════════════════════════════════════ */
.stRadio > label { font-weight: 600; color: #374151; font-size: .83rem; }

/* ═══ SLIDER ══════════════════════════════════════════════════════════════════ */
.stSlider [data-baseweb="slider"] { padding: 0; }
[data-testid="stSlider"] > div > div > div > div {
    background: #7C3AED !important;
}

/* ═══ FOOTER ══════════════════════════════════════════════════════════════════ */
.dataviz-footer {
    margin-top: 3rem;
    padding: 1.5rem 0 .5rem;
    border-top: 1px solid #E2E8F0;
    text-align: center;
}
.dataviz-footer a {
    color: #7C3AED;
    text-decoration: none;
    font-size: .8rem;
    font-weight: 500;
    margin: 0 .6rem;
}
.dataviz-footer a:hover { text-decoration: underline; }
.dataviz-footer p {
    color: #94A3B8;
    font-size: .75rem;
    margin-top: .5rem;
}

/* ═══ SECTION LABEL ═══════════════════════════════════════════════════════════ */
.section-label {
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #7C3AED;
    margin-bottom: .5rem;
}

/* ═══ CARD ════════════════════════════════════════════════════════════════════ */
.card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
    border: 1px solid #F1F5F9;
}

/* ════════════════════════════════════════════════════════════════════════════
   MOBILE — max-width: 768px
   ════════════════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .main .block-container {
        padding: .8rem 1rem 2rem !important;
    }
    .page-header h2 { font-size: 1.25rem !important; }
    div[data-testid="stMetricValue"] { font-size: 1.25rem !important; }

    /* Stack columns on mobile */
    [data-testid="column"] {
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: .32rem .6rem !important;
        font-size: .74rem !important;
    }

    /* Bigger touch targets */
    .stButton > button,
    .stDownloadButton > button {
        min-height: 48px !important;
        font-size: .85rem !important;
        width: 100% !important;
    }

    .stSelectbox [data-baseweb="select"] > div,
    .stTextInput > div > div > input {
        min-height: 48px !important;
        font-size: .9rem !important;
    }

    [data-testid="stSidebar"] {
        min-width: 220px !important;
        max-width: 220px !important;
    }
}

/* ════════════════════════════════════════════════════════════════════════════
   SMALL MOBILE — max-width: 480px
   ════════════════════════════════════════════════════════════════════════════ */
@media (max-width: 480px) {
    .main .block-container {
        padding: .6rem .7rem 2rem !important;
    }
    .page-header h2 { font-size: 1.1rem !important; }
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 1px !important; }
}
</style>
""", unsafe_allow_html=True)

for k, v in [("raw_df", None), ("df", None), ("filename", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:.8rem 1rem 1rem;'>
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:1.2rem;'>
            <div style='width:36px;height:36px;
                        background:linear-gradient(135deg,#7C3AED,#F43F5E);
                        border-radius:9px;display:flex;align-items:center;
                        justify-content:center;font-size:1rem;flex-shrink:0;'>📊</div>
            <div>
                <div style='font-size:.95rem;font-weight:800;color:#0F172A;'>DataViz Pro</div>
                <div style='font-size:.68rem;color:#9CA3AF;font-weight:500;'>Advanced Analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = option_menu(
        menu_title=None,
        options=[
            "Home", "Upload Data", "Data Profiling", "Data Cleaning",
            "EDA & Statistics", "Chart Builder", "Auto Dashboard",
            "Time Series", "ML Insights", "Ask Your Data", "Export & Reports",
            "─────────────",
            "Privacy Policy", "Terms of Service", "Cookie Policy",
        ],
        icons=[
            "house-heart-fill", "cloud-arrow-up-fill", "clipboard2-data-fill",
            "magic", "graph-up-arrow", "bar-chart-fill", "speedometer2",
            "calendar3", "cpu-fill", "chat-dots-fill", "box-arrow-up-right",
            "dash",
            "shield-lock-fill", "file-text-fill", "cookie",
        ],
        default_index=0,
        styles={
            "container":         {"padding": "0 .4rem", "background-color": "transparent"},
            "icon":              {"color": "#7C3AED", "font-size": "13px"},
            "nav-link":          {
                "font-size": "12.5px", "font-weight": "600",
                "padding": ".48rem .85rem", "border-radius": "8px",
                "margin": "1px 0", "color": "#374151",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg,#EDE9FE,#FCE7F3)",
                "color": "#7C3AED", "font-weight": "800",
            },
            "nav-link-disabled": {"color": "#CBD5E1 !important", "cursor": "default"},
        },
    )

    st.markdown("<div style='height:1px;background:#E2E8F0;margin:.8rem .4rem'></div>",
                unsafe_allow_html=True)

    if st.session_state.df is not None:
        r, c = st.session_state.df.shape
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#F5F3FF,#FDF2F8);
                    border:1.5px solid #DDD6FE;border-radius:10px;padding:.8rem 1rem;
                    margin:0 .4rem;'>
            <div style='font-size:.62rem;font-weight:800;color:#7C3AED;
                        text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;'>
                Active Dataset
            </div>
            <div style='font-size:.8rem;font-weight:700;color:#0F172A;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>
                {st.session_state.filename}
            </div>
            <div style='font-size:.72rem;color:#9CA3AF;margin-top:2px;'>
                {r:,} rows &middot; {c} cols
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#F9FAFB;border:1.5px dashed #DDD6FE;
                    border-radius:10px;padding:.8rem 1rem;text-align:center;
                    margin:0 .4rem;'>
            <div style='font-size:.78rem;color:#9CA3AF;'>No dataset loaded</div>
            <div style='font-size:.72rem;color:#7C3AED;font-weight:700;margin-top:2px;'>
                Upload Data to start →
            </div>
        </div>""", unsafe_allow_html=True)

# ── Footer helper ──────────────────────────────────────────────────────────────
def _footer():
    st.markdown("""
    <div class='dataviz-footer'>
        <a href='#' onclick="window.parent.document.querySelector('[title=\\"Privacy Policy\\"]').click()">
            Privacy Policy
        </a>
        <a href='#' onclick="window.parent.document.querySelector('[title=\\"Terms of Service\\"]').click()">
            Terms of Service
        </a>
        <a href='#' onclick="window.parent.document.querySelector('[title=\\"Cookie Policy\\"]').click()">
            Cookie Policy
        </a>
        <p>© 2025 DataViz Pro · All rights reserved</p>
    </div>
    """, unsafe_allow_html=True)


# ── Router ─────────────────────────────────────────────────────────────────────
_SEPARATOR = "─────────────"

if page == _SEPARATOR:
    st.info("Please select a page from the menu.")
else:
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
    if page in _ROUTES:
        _ROUTES[page]()

_footer()
