import streamlit as st
from streamlit_option_menu import option_menu
from styles import DARK_CSS, SIDEBAR_CSS

st.set_page_config(
    page_title="DataViz Pro",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from home import home_page
from filesin import file_upload
from dataover import data_overview
from profiling import data_profiling
from eda_page import eda_page
from dashgen import generate_dash_app
from editdash import edit_dashboard
from ml_page import ml_insights

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(DARK_CSS + SIDEBAR_CSS, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <span class="sidebar-logo-icon">⬡</span>
      <span class="sidebar-logo-text">DataViz<span>Pro</span></span>
    </div>
    """, unsafe_allow_html=True)

    # Dataset badge
    has_data = "clean_data" in st.session_state and st.session_state["clean_data"] is not None
    if has_data:
        df = st.session_state["clean_data"]
        fname = st.session_state.get("filename", "dataset")
        st.markdown(f"""
        <div class="ds-card">
          <div class="ds-card-name">📁 {fname[:24]}</div>
          <div class="ds-card-stats">{df.shape[0]:,} rows · {df.shape[1]} cols</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="ds-card ds-card-empty">
          <div class="ds-card-name">📭 No dataset loaded</div>
          <div class="ds-card-stats">Upload to get started</div>
        </div>
        """, unsafe_allow_html=True)

    # Nav
    nav_override = st.session_state.pop("nav", None)

    nav_options = [
        "Home",
        "File Upload",
        "Data Overview",
        "Data Profiling",
        "EDA & Statistics",
        "Dashboard Generator",
        "Chart Builder",
        "ML Insights",
    ]

    nav_icons = [
        "house-fill",
        "cloud-upload",
        "table",
        "search",
        "graph-up",
        "bar-chart-line",
        "pencil-square",
        "cpu",
    ]

    default_idx = 0
    if nav_override and nav_override in nav_options:
        default_idx = nav_options.index(nav_override)

    app = option_menu(
        menu_title=None,
        options=nav_options,
        icons=nav_icons,
        menu_icon="bookmark-star",
        default_index=default_idx,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#94A3B8", "font-size": "15px"},
            "nav-link": {
                "font-size": "14px",
                "color": "#94A3B8",
                "padding": "8px 12px",
                "--hover-color": "rgba(255,255,255,0.05)",
            },
            "nav-link-selected": {
                "background-color": "rgba(0,212,255,0.1)",
                "color": "#00D4FF",
                "font-weight": "600",
            },
        },
    )

    # Bottom info
    st.markdown("---")
    st.markdown('<div style="font-size:.72rem;color:#475569;padding:.25rem 0;">⬡ DataViz Pro — v2.0</div>', unsafe_allow_html=True)

# ── Page routing ───────────────────────────────────────────────────────────────
if app == "Home":
    home_page()
elif app == "File Upload":
    file_upload()
elif app == "Data Overview":
    data_overview()
elif app == "Data Profiling":
    data_profiling()
elif app == "EDA & Statistics":
    eda_page()
elif app == "Dashboard Generator":
    generate_dash_app()
elif app == "Chart Builder":
    edit_dashboard()
elif app == "ML Insights":
    ml_insights()
