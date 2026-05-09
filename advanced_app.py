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

st.set_page_config(
    page_title="DataViz Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

*, html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }

/* ═══ APP SHELL ═══════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] > .main {
    background: #FAFAF9;
}
.main .block-container {
    padding: 2rem 2.5rem 3rem;
    max-width: 1440px;
}

/* ═══ SIDEBAR ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #EDE9FE;
}
[data-testid="stSidebar"] * { color: #374151 !important; }

/* ═══ PAGE HEADER (used by all pages) ════════════════════════════════ */
.ph-wrap { margin-bottom: 2rem; }
.ph-eyebrow {
    font-size: 0.7rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: #7C3AED; margin-bottom: 4px;
}
.ph-title {
    font-size: 1.75rem; font-weight: 800; color: #1C1917;
    line-height: 1.15; margin: 0;
}
.ph-bar {
    width: 48px; height: 4px;
    background: linear-gradient(90deg,#7C3AED,#F43F5E);
    border-radius: 2px; margin: 10px 0;
}
.ph-sub { font-size: 0.875rem; color: #6B7280; margin: 0; }

/* ═══ METRIC CARDS ════════════════════════════════════════════════════ */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #EDE9FE;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 1px 3px rgba(124,58,237,.07);
}
div[data-testid="stMetricLabel"]  { color: #6B7280 !important; font-size: 0.78rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing:.04em; }
div[data-testid="stMetricValue"]  { color: #1C1917 !important; font-size: 1.65rem !important; font-weight: 800 !important; }

/* ═══ TABS ════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #F5F3FF;
    border-radius: 10px;
    padding: 4px;
    border: none;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px; padding: 0.4rem 1rem;
    font-size: 0.83rem; font-weight: 600;
    color: #6B7280 !important; background: transparent; border: none;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #7C3AED !important;
    box-shadow: 0 1px 4px rgba(124,58,237,.15);
}

/* ═══ BUTTONS ══════════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg,#7C3AED,#9333EA);
    color: white !important; border: none;
    border-radius: 9px; padding: .5rem 1.3rem;
    font-weight: 700; font-size: .84rem;
    box-shadow: 0 2px 8px rgba(124,58,237,.3);
    transition: all .15s;
}
.stButton > button:hover {
    background: linear-gradient(135deg,#6D28D9,#7C3AED);
    box-shadow: 0 4px 14px rgba(124,58,237,.4);
    transform: translateY(-1px);
    color: white !important;
}
.stButton > button[kind="secondary"] {
    background: #FFFFFF; color: #7C3AED !important;
    border: 1.5px solid #DDD6FE;
    box-shadow: none;
}

/* ═══ DOWNLOAD BUTTONS ════════════════════════════════════════════════ */
.stDownloadButton > button {
    background: linear-gradient(135deg,#F43F5E,#E11D48);
    color: white !important; border: none; border-radius: 9px;
    font-weight: 700; padding: .5rem 1.3rem;
    box-shadow: 0 2px 8px rgba(244,63,94,.3);
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg,#E11D48,#BE123C);
    box-shadow: 0 4px 14px rgba(244,63,94,.4);
    transform: translateY(-1px); color: white !important;
}

/* ═══ INPUTS ══════════════════════════════════════════════════════════ */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput > div > div > input {
    background: #FFFFFF; border: 1.5px solid #DDD6FE;
    border-radius: 8px; color: #1C1917;
}
.stTextInput > div > div > input:focus { border-color: #7C3AED; }

/* ═══ ALERTS ══════════════════════════════════════════════════════════ */
.stAlert { border-radius: 10px; font-size: .875rem; }

/* ═══ EXPANDER ════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: #FFFFFF; border: 1.5px solid #EDE9FE;
    border-radius: 9px; font-weight: 700; color: #1C1917;
}

/* ═══ DATAFRAME ═══════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #EDE9FE; }

/* ═══ RADIO / CHECKBOX ════════════════════════════════════════════════ */
.stRadio > label { font-weight: 600; color: #374151; font-size: .83rem; }

/* ═══ SLIDER ══════════════════════════════════════════════════════════ */
.stSlider [data-baseweb="slider"] { padding: 0; }

/* ═══ PAGE HEADER (legacy .page-header used by modules) ══════════════ */
.page-header {
    margin-bottom: 1.8rem;
    padding-bottom: .3rem;
}
.page-header h2 {
    font-size: 1.65rem; font-weight: 800; color: #1C1917;
    margin: 0 0 6px;
}
.page-header::after {
    content: ''; display: block; width: 44px; height: 4px;
    background: linear-gradient(90deg,#7C3AED,#F43F5E);
    border-radius: 2px; margin: 8px 0 8px;
}
.page-header p { font-size: .875rem; color: #6B7280; margin: 0; }

/* ═══ CARD UTILITY ════════════════════════════════════════════════════ */
.card {
    background: #FFFFFF; border-radius: 14px;
    padding: 1.3rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
    border: 1px solid #F3F4F6;
}
.tag {
    display:inline-block; border-radius:20px;
    padding:.25rem .75rem; font-size:.75rem; font-weight:700;
}
</style>
""", unsafe_allow_html=True)

for k, v in [("raw_df", None), ("df", None), ("filename", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:.8rem 1rem 1rem;'>
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:1rem;'>
            <div style='width:38px;height:38px;
                        background:linear-gradient(135deg,#7C3AED,#F43F5E);
                        border-radius:10px;display:flex;align-items:center;
                        justify-content:center;font-size:1.1rem;'>📊</div>
            <div>
                <div style='font-size:1rem;font-weight:800;color:#1C1917;'>DataViz Pro</div>
                <div style='font-size:.7rem;color:#9CA3AF;font-weight:500;'>Advanced Analytics</div>
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
        ],
        icons=[
            "house-heart-fill", "cloud-arrow-up-fill", "clipboard2-data-fill",
            "magic", "graph-up-arrow", "bar-chart-fill", "speedometer",
            "calendar3", "cpu-fill", "chat-dots-fill", "box-arrow-up-right",
        ],
        default_index=0,
        styles={
            "container":         {"padding": "0 .5rem", "background-color": "transparent"},
            "icon":              {"color": "#7C3AED", "font-size": "14px"},
            "nav-link":          {
                "font-size": "13px", "font-weight": "600",
                "padding": ".52rem .9rem", "border-radius": "9px",
                "margin": "1px 0", "color": "#374151",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg,#EDE9FE,#FCE7F3)",
                "color": "#7C3AED", "font-weight": "800",
            },
        },
    )

    st.markdown("<div style='height:1px;background:#EDE9FE;margin:.8rem 0'></div>",
                unsafe_allow_html=True)

    if st.session_state.df is not None:
        r, c = st.session_state.df.shape
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#F5F3FF,#FDF2F8);
                    border:1.5px solid #DDD6FE;border-radius:12px;padding:.9rem 1rem;'>
            <div style='font-size:.66rem;font-weight:800;color:#7C3AED;
                        text-transform:uppercase;letter-spacing:.08em;margin-bottom:5px;'>Active Dataset</div>
            <div style='font-size:.83rem;font-weight:700;color:#1C1917;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{st.session_state.filename}</div>
            <div style='font-size:.74rem;color:#9CA3AF;margin-top:3px;'>{r:,} rows &middot; {c} cols</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#F9FAFB;border:1.5px dashed #DDD6FE;
                    border-radius:12px;padding:.9rem 1rem;text-align:center;'>
            <div style='font-size:.8rem;color:#9CA3AF;'>No dataset loaded</div>
            <div style='font-size:.74rem;color:#7C3AED;font-weight:700;margin-top:2px;'>
                → Upload Data to start</div>
        </div>""", unsafe_allow_html=True)

# ── Router ───────────────────────────────────────────────────────────────
{
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
}[page]()
