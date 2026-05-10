import streamlit as st
from streamlit_option_menu import option_menu
from styles import DARK_CSS, SIDEBAR_CSS
from shared_store import get_meta as bridge_meta, load_shared, bridge_exists

st.set_page_config(
    page_title="DataViz Pro",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from home import home_page
from filesin import file_upload
from connector import connect_page
from dataover import data_overview
from quality import data_quality_page
from profiling import data_profiling
from eda_page import eda_page
from viz_tools import viz_tools_page
from dashgen import generate_dash_app
from editdash import edit_dashboard
from ml_page import ml_insights
from export_share import export_share_page
from nlq_page import nlq_page

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

    # Bridge sync — show if Flask has data we haven't loaded yet
    if bridge_exists():
        meta = bridge_meta()
        if meta and meta.get("source") == "flask":
            bridge_file = meta.get("filename", "")
            session_file = st.session_state.get("filename", "")
            if bridge_file != session_file:
                st.markdown(f"""
                <div style="background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.2);
                            border-radius:6px;padding:.5rem .75rem;margin:.5rem 0;
                            font-size:.75rem;color:#94A3B8;">
                  <span style="color:#00D4FF;">⟳</span>
                  Flask: <b style="color:#E2E8F0;">{bridge_file}</b>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Sync from Flask", use_container_width=True, key="sidebar_sync_btn"):
                    df_bridge, _ = load_shared()
                    if df_bridge is not None:
                        st.session_state["raw_data"]   = df_bridge.copy()
                        st.session_state["clean_data"] = df_bridge.copy()
                        st.session_state["filename"]   = bridge_file
                        st.rerun()

    # Nav
    nav_override = st.session_state.pop("nav", None)

    nav_options = [
        "Home",
        "File Upload",
        "Connect & Import",
        "Data Overview",
        "Data Quality",
        "Data Profiling",
        "EDA & Statistics",
        "Natural Language Query",
        "Visualization Tools",
        "Dashboard Generator",
        "Chart Builder",
        "ML Insights",
        "Export & Share",
    ]

    nav_icons = [
        "house-fill",
        "cloud-upload",
        "plug",
        "table",
        "shield-check",
        "search",
        "graph-up",
        "chat-dots",
        "palette",
        "bar-chart-line",
        "pencil-square",
        "cpu",
        "share",
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
elif app == "Connect & Import":
    connect_page()
elif app == "Data Overview":
    data_overview()
elif app == "Data Quality":
    data_quality_page()
elif app == "Data Profiling":
    data_profiling()
elif app == "EDA & Statistics":
    eda_page()
elif app == "Natural Language Query":
    nlq_page()
elif app == "Visualization Tools":
    viz_tools_page()
elif app == "Dashboard Generator":
    generate_dash_app()
elif app == "Chart Builder":
    edit_dashboard()
elif app == "ML Insights":
    ml_insights()
elif app == "Export & Share":
    export_share_page()
