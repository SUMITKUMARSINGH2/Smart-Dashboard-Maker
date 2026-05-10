import streamlit as st
from styles import DARK_CSS, SIDEBAR_CSS, section_header, kpi_row_html, badge

def home_page():
    st.markdown(DARK_CSS + SIDEBAR_CSS, unsafe_allow_html=True)
    st.markdown(section_header("⬡", "DataViz Pro", "Advanced no-code data analytics platform"), unsafe_allow_html=True)

    has_data = "clean_data" in st.session_state and st.session_state["clean_data"] is not None

    # Hero
    if not has_data:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem 2rem;">
          <div style="display:inline-flex;align-items:center;gap:.4rem;background:rgba(0,212,255,.08);
                      border:1px solid rgba(0,212,255,.2);border-radius:999px;padding:.35rem 1rem;
                      font-size:.8rem;color:#00D4FF;margin-bottom:1.5rem;">
            ⬡ Advanced Data Analytics Platform
          </div>
          <h1 style="font-size:clamp(2rem,5vw,3.2rem);font-weight:700;line-height:1.1;
                     margin-bottom:1rem;color:#E2E8F0;">
            Turn Raw Data Into<br><span style="color:#00D4FF;">Powerful Insights</span>
          </h1>
          <p style="color:#94A3B8;font-size:1.05rem;max-width:580px;margin:0 auto 2rem;line-height:1.7;">
            Upload any dataset — CSV, Excel, JSON, Parquet — and instantly explore, clean, 
            visualize, and model your data with zero code required.
          </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Get Started — Upload Data", use_container_width=True):
                st.session_state["nav"] = "File upload"
                st.rerun()
    else:
        df = st.session_state["clean_data"]
        import pandas as pd
        num_cols = df.select_dtypes(include=["int64","float64","int32","float32"]).shape[1]
        cat_cols = df.select_dtypes(include=["object","category"]).shape[1]
        missing = int(df.isnull().sum().sum())
        dups = int(df.duplicated().sum())
        missing_pct = round(missing / (df.shape[0]*df.shape[1]) * 100, 1) if df.shape[0]*df.shape[1] > 0 else 0

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(0,212,255,.06),rgba(124,58,237,.06));
                    border:1px solid rgba(0,212,255,.18);border-radius:10px;
                    padding:1.25rem 1.5rem;margin-bottom:.5rem;">
          <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.25rem;">
            <span style="color:#10B981;font-size:.85rem;">●</span>
            <span style="font-weight:700;color:#E2E8F0;font-size:1rem;">
              {st.session_state.get("filename","dataset")} — Dataset Loaded
            </span>
          </div>
          <div style="color:#94A3B8;font-size:.82rem;">
            Ready to analyze · {df.shape[0]:,} rows · {df.shape[1]} columns
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(kpi_row_html([
            ("Total Rows", f"{df.shape[0]:,}"),
            ("Columns", df.shape[1]),
            ("Numeric", num_cols),
            ("Categorical", cat_cols),
            ("Missing", f"{missing:,}"),
            ("Duplicates", dups),
        ]), unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("◎ Profile Data", use_container_width=True):
                st.session_state["nav"] = "Data Profiling"
                st.rerun()
        with c2:
            if st.button("∿ EDA & Stats", use_container_width=True):
                st.session_state["nav"] = "EDA & Statistics"
                st.rerun()
        with c3:
            if st.button("⚡ Dashboard", use_container_width=True):
                st.session_state["nav"] = "Dashboard Generator"
                st.rerun()
        with c4:
            if st.button("▦ Chart Builder", use_container_width=True):
                st.session_state["nav"] = "Edit Dashboard"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    st.markdown('<div style="font-size:.7rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#475569;margin-bottom:1rem;">Platform Features</div>', unsafe_allow_html=True)

    features = [
        ("⬆", "Smart Upload", "CSV, Excel, JSON, Parquet, TSV with auto type detection."),
        ("◎", "Data Profiling", "Per-column statistics, distributions, and quality scores."),
        ("✦", "Data Cleaning", "Remove duplicates, fill nulls, cast types, filter rows."),
        ("∿", "EDA & Statistics", "Correlations, distributions, box plots, hypothesis tests."),
        ("▦", "Chart Builder", "Build custom charts: bar, scatter, pie, heatmap, violin."),
        ("⚡", "Auto Dashboard", "Auto-generate KPIs and smart charts from your data."),
        ("⏱", "Time Series", "Trend analysis, rolling averages, seasonal decomposition."),
        ("◈", "ML Insights", "Clustering, anomaly detection, PCA, feature importance."),
        ("◑", "Forecasting", "ARIMA and exponential smoothing forecasts."),
        ("↓", "Export", "Download cleaned data as CSV with one click."),
    ]

    cols_per_row = 5
    for row_start in range(0, len(features), cols_per_row):
        row_features = features[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, (icon, title, desc) in enumerate(row_features):
            with cols[i]:
                st.markdown(f"""
                <div style="background:#0D1528;border:1px solid #1E293B;border-radius:10px;
                            padding:1.2rem;height:100%;transition:all .2s;">
                  <div style="font-size:1.5rem;margin-bottom:.6rem;">{icon}</div>
                  <div style="font-weight:600;color:#E2E8F0;margin-bottom:.4rem;font-size:.9rem;">{title}</div>
                  <div style="color:#94A3B8;font-size:.78rem;line-height:1.5;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    # Tabs: Intro / Workflow / Support
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📘 How It Works", "🚀 Roadmap", "💬 Support"])

    with tab1:
        st.markdown("""
        <div style="background:#0D1528;border:1px solid #1E293B;border-radius:10px;padding:1.5rem;line-height:1.8;">
          <b style="color:#00D4FF;">✅ Workflow in 4 steps:</b><br><br>
          <b style="color:#E2E8F0;">1. Upload</b> <span style="color:#94A3B8;">— Drag and drop your CSV, Excel, JSON, or Parquet file.</span><br>
          <b style="color:#E2E8F0;">2. Profile & Clean</b> <span style="color:#94A3B8;">— Inspect column types, handle missing values and duplicates.</span><br>
          <b style="color:#E2E8F0;">3. Explore & Visualize</b> <span style="color:#94A3B8;">— Run EDA, build charts, and auto-generate dashboards.</span><br>
          <b style="color:#E2E8F0;">4. Model & Export</b> <span style="color:#94A3B8;">— Apply ML insights, forecasting, and download your results.</span>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div style="background:#0D1528;border:1px solid #1E293B;border-radius:10px;padding:1.5rem;line-height:1.8;">
          <b style="color:#7C3AED;">🌟 Coming Soon:</b><br><br>
          <span style="color:#94A3B8;">
          🤖 AutoML with model comparison<br>
          ⏳ Advanced time series forecasting (Prophet)<br>
          📈 Smart chart recommendations<br>
          🖼️ Dashboard templates library<br>
          ☁️ Cloud storage and live data APIs<br>
          👥 Collaboration and sharing features
          </span>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        with st.form("support_form", clear_on_submit=True):
            st.markdown('<div style="color:#94A3B8;margin-bottom:1rem;">Need help? Fill out the form below.</div>', unsafe_allow_html=True)
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Message", height=120)
            submitted = st.form_submit_button("Send Message")
            if submitted:
                if name and email and message:
                    st.success("✅ Thank you! Your message has been received.")
                else:
                    st.error("⚠️ Please fill in all fields before submitting.")
