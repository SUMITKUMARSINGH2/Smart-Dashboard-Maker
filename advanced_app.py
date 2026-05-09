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

st.set_page_config(
    page_title="DataViz Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Sidebar ─────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0F172A !important;
    border-right: 1px solid #1E293B;
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] .stMarkdown p { color: #64748B !important; font-size: 0.75rem; }

/* ── Main content area ───────────────────── */
.main .block-container {
    padding: 1.8rem 2.2rem 2rem;
    max-width: 1400px;
}
[data-testid="stAppViewContainer"] > .main {
    background: #F1F5F9;
}

/* ── Page header ─────────────────────────── */
.page-header {
    background: #FFFFFF;
    border-left: 4px solid #0EA5E9;
    padding: 1rem 1.6rem;
    border-radius: 0 10px 10px 0;
    margin-bottom: 1.6rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.page-header h2 { margin: 0; color: #0F172A; font-size: 1.4rem; font-weight: 700; }
.page-header p  { margin: 0.2rem 0 0; color: #64748B; font-size: 0.85rem; }

/* ── Metric cards ────────────────────────── */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
div[data-testid="stMetricLabel"]  { color: #64748B !important; font-size: 0.78rem !important; }
div[data-testid="stMetricValue"]  { color: #0F172A !important; font-size: 1.5rem !important; font-weight: 700 !important; }
div[data-testid="stMetricDelta"]  { font-size: 0.8rem !important; }

/* ── Tabs ─────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 2px solid #E2E8F0; }
.stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0;
    padding: 0.45rem 1.1rem;
    font-size: 0.85rem;
    font-weight: 500;
    color: #64748B !important;
    background: transparent;
    border: none;
}
.stTabs [aria-selected="true"] {
    color: #0EA5E9 !important;
    border-bottom: 2px solid #0EA5E9 !important;
    background: #F0F9FF !important;
}

/* ── Buttons ─────────────────────────────── */
.stButton > button {
    background: #0EA5E9;
    color: white;
    border: none;
    border-radius: 7px;
    padding: 0.45rem 1.1rem;
    font-weight: 500;
    font-size: 0.85rem;
    transition: background 0.15s;
}
.stButton > button:hover { background: #0284C7; color: white; }
.stButton > button[kind="secondary"] {
    background: #F1F5F9;
    color: #334155;
    border: 1px solid #CBD5E1;
}

/* ── Download buttons ────────────────────── */
.stDownloadButton > button {
    background: #F59E0B;
    color: white;
    border: none;
    border-radius: 7px;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
}
.stDownloadButton > button:hover { background: #D97706; color: white; }

/* ── Selectbox / Input ───────────────────── */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput > div > div > input {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 7px;
}

/* ── Info / Warning / Success ────────────── */
.stAlert { border-radius: 8px; font-size: 0.875rem; }

/* ── Expander ────────────────────────────── */
.streamlit-expanderHeader {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    font-weight: 600;
    color: #0F172A;
}

/* ── Dataframe ───────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* ── Section divider label ───────────────── */
.section-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #475569;
    font-weight: 600;
    margin: 1.2rem 0 0.4rem;
}

/* ── Stat card ───────────────────────────── */
.stat-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.3rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border-top: 3px solid transparent;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

for key, val in [("raw_df", None), ("df", None), ("filename", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0.5rem 0.5rem; border-bottom: 1px solid #1E293B; margin-bottom: 0.8rem;'>
        <div style='display:flex; align-items:center; gap:10px;'>
            <div style='width:34px;height:34px;background:#0EA5E9;border-radius:8px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:18px;'>📊</div>
            <div>
                <div style='color:#F1F5F9;font-weight:700;font-size:1rem;line-height:1.2'>DataViz Pro</div>
                <div style='color:#475569;font-size:0.7rem;'>Advanced Analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = option_menu(
        menu_title=None,
        options=[
            "Home", "Upload Data", "Data Profiling", "Data Cleaning",
            "EDA & Statistics", "Chart Builder", "Auto Dashboard",
            "Time Series", "Export & Reports",
        ],
        icons=[
            "house", "cloud-upload", "clipboard-data", "tools",
            "graph-up", "bar-chart", "speedometer2",
            "clock-history", "box-arrow-up",
        ],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#0EA5E9", "font-size": "14px"},
            "nav-link": {
                "font-size": "13.5px",
                "font-weight": "500",
                "text-align": "left",
                "padding": "0.55rem 1rem",
                "border-radius": "7px",
                "margin": "1px 0",
                "color": "#94A3B8",
            },
            "nav-link-selected": {
                "background-color": "#1E3A5F",
                "color": "#FFFFFF",
                "font-weight": "600",
            },
        },
    )

    st.markdown("<div style='height:1px;background:#1E293B;margin:0.8rem 0'></div>", unsafe_allow_html=True)

    if st.session_state.df is not None:
        r, c = st.session_state.df.shape
        st.markdown(f"""
        <div style='background:#132035;border:1px solid #1E3A5F;border-radius:8px;padding:0.8rem 1rem;'>
            <div style='color:#0EA5E9;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px'>Active Dataset</div>
            <div style='color:#E2E8F0;font-size:0.85rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{st.session_state.filename}</div>
            <div style='color:#475569;font-size:0.75rem;margin-top:3px'>{r:,} rows &middot; {c} columns</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#132035;border:1px dashed #1E3A5F;border-radius:8px;padding:0.8rem 1rem;text-align:center;'>
            <div style='color:#475569;font-size:0.8rem;'>No dataset loaded</div>
            <div style='color:#0EA5E9;font-size:0.75rem;margin-top:2px;'>Go to Upload Data →</div>
        </div>
        """, unsafe_allow_html=True)

dispatch = {
    "Home": home_page, "Upload Data": upload_page,
    "Data Profiling": profiling_page, "Data Cleaning": cleaning_page,
    "EDA & Statistics": eda_page, "Chart Builder": visualizations_page,
    "Auto Dashboard": dashboard_page, "Time Series": timeseries_page,
    "Export & Reports": export_page,
}
dispatch[page]()
