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
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29, #302b63, #24243e);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { margin: 0; font-size: 1.8rem; }
    .main-header p { margin: 0.3rem 0 0; opacity: 0.85; font-size: 0.95rem; }
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        text-align: center;
    }
    .kpi-card h3 { margin: 0; color: #333; font-size: 1.8rem; }
    .kpi-card p { margin: 0.3rem 0 0; color: #666; font-size: 0.85rem; }
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.2rem;
    }
    .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "df" not in st.session_state:
    st.session_state.df = None
if "filename" not in st.session_state:
    st.session_state.filename = None

with st.sidebar:
    st.markdown("### 🔬 DataViz Pro")
    st.markdown("---")
    page = option_menu(
        menu_title=None,
        options=[
            "Home",
            "Upload Data",
            "Data Profiling",
            "Data Cleaning",
            "EDA & Statistics",
            "Chart Builder",
            "Auto Dashboard",
            "Time Series",
            "Export",
        ],
        icons=[
            "house-fill",
            "cloud-upload-fill",
            "clipboard-data-fill",
            "tools",
            "graph-up",
            "bar-chart-fill",
            "speedometer2",
            "clock-history",
            "download",
        ],
        menu_icon=None,
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#a78bfa", "font-size": "16px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "padding": "0.55rem 1rem",
                "border-radius": "8px",
                "margin": "2px 0",
                "color": "#e0e0e0",
            },
            "nav-link-selected": {
                "background-color": "rgba(102,126,234,0.35)",
                "color": "white",
                "font-weight": "600",
            },
        },
    )
    st.markdown("---")
    if st.session_state.df is not None:
        st.success(f"📂 {st.session_state.filename}")
        r, c = st.session_state.df.shape
        st.caption(f"{r:,} rows · {c} columns")
    else:
        st.info("No data loaded yet")

if page == "Home":
    home_page()
elif page == "Upload Data":
    upload_page()
elif page == "Data Profiling":
    profiling_page()
elif page == "Data Cleaning":
    cleaning_page()
elif page == "EDA & Statistics":
    eda_page()
elif page == "Chart Builder":
    visualizations_page()
elif page == "Auto Dashboard":
    dashboard_page()
elif page == "Time Series":
    timeseries_page()
elif page == "Export":
    export_page()
