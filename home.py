import streamlit as st
from styles import DARK_CSS, SIDEBAR_CSS, section_header, kpi_row_html, badge
from shared_store import load_shared, get_meta as bridge_meta, bridge_exists

def home_page():
    st.markdown(DARK_CSS + SIDEBAR_CSS, unsafe_allow_html=True)

    has_data = "clean_data" in st.session_state and st.session_state["clean_data"] is not None

    # ── Bridge sync banner ─────────────────────────────────────────────────────
    if bridge_exists():
        meta = bridge_meta()
        if meta:
            session_file = st.session_state.get("filename", "")
            bridge_file  = meta.get("filename", "")
            bridge_src   = meta.get("source", "")
            bridge_rows  = meta.get("rows", 0)
            if bridge_src == "flask" and bridge_file != session_file:
                st.markdown(f"""
                <div style="background:rgba(56,189,248,.06);border:1px solid rgba(56,189,248,.2);
                            border-radius:10px;padding:.65rem 1rem;margin-bottom:1rem;
                            display:flex;align-items:center;gap:.6rem;font-size:.83rem;color:#94a3b8;">
                  <span style="color:#38bdf8;">⟳</span>
                  Flask loaded <b style="color:#e8eaf6;">{bridge_file}</b> ({bridge_rows:,} rows). Sync it?
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"⟳  Sync \"{bridge_file}\" from Flask"):
                    df, _ = load_shared()
                    if df is not None:
                        st.session_state["raw_data"]   = df.copy()
                        st.session_state["clean_data"] = df.copy()
                        st.session_state["filename"]   = bridge_file
                        st.rerun()
                    else:
                        st.error("Could not read bridge file.")

    # ── Hero ───────────────────────────────────────────────────────────────────
    if not has_data:
        st.markdown("""
        <style>
        @keyframes rainbowFlow {
          0%   { background-position: 0% center; }
          100% { background-position: 200% center; }
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(20px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes bobble {
          0%, 100% { transform: translateY(0px); }
          50%       { transform: translateY(-4px); }
        }

        .hero-outer {
          text-align: center;
          padding: 4rem 1rem 3rem;
          animation: fadeUp .6s ease both;
        }

        .hero-badge {
          display: inline-block;
          background: rgba(99,102,241,.12);
          border: 1px solid rgba(99,102,241,.3);
          border-radius: 999px;
          padding: .38rem 1.1rem;
          font-size: .78rem;
          font-weight: 600;
          color: #818cf8;
          margin-bottom: 2rem;
          animation: bobble 3s ease-in-out infinite;
          letter-spacing: .04em;
        }

        .hero-top {
          font-size: clamp(2.4rem, 5.5vw, 3.8rem);
          font-weight: 900;
          color: #e8eaf6;
          line-height: 1.05;
          letter-spacing: -2px;
          margin-bottom: .15rem;
        }

        .hero-rainbow {
          font-size: clamp(2.4rem, 5.5vw, 3.8rem);
          font-weight: 900;
          letter-spacing: -2px;
          line-height: 1.15;
          margin-bottom: 1.6rem;

          background: linear-gradient(
            90deg,
            #ff0000, #ff6600, #ffcc00,
            #00ff88, #00cfff, #6600ff,
            #ff00cc, #ff0000
          );
          background-size: 300% auto;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: rainbowFlow 1.5s linear infinite;
          display: block;
        }

        .hero-sub {
          color: #6b7280;
          font-size: 1rem;
          max-width: 520px;
          margin: 0 auto 2.2rem;
          line-height: 1.8;
        }

        .hero-chips {
          display: flex;
          flex-wrap: wrap;
          justify-content: center;
          gap: .45rem;
          margin-bottom: 2.2rem;
        }
        .hero-chip {
          background: rgba(255,255,255,.04);
          border: 1px solid #1f2937;
          border-radius: 999px;
          padding: .28rem .85rem;
          font-size: .72rem;
          color: #6b7280;
          font-weight: 500;
        }
        </style>

        <div class="hero-outer">
          <div class="hero-badge">✦ Advanced Data Analytics Platform</div>
          <div class="hero-top">Turn Raw Data Into</div>
          <span class="hero-rainbow">Powerful Insights</span>
          <p class="hero-sub">
            Upload any dataset — CSV, Excel, JSON, Parquet — and instantly
            explore, clean, visualize, and model your data with zero code required.
          </p>
          <div class="hero-chips">
            <span class="hero-chip">📊 CSV &amp; Excel</span>
            <span class="hero-chip">📁 JSON &amp; Parquet</span>
            <span class="hero-chip">🤖 ML Insights</span>
            <span class="hero-chip">📈 Auto Dashboard</span>
            <span class="hero-chip">⏱ Time Series</span>
            <span class="hero-chip">◑ Forecasting</span>
            <span class="hero-chip">✦ Data Cleaning</span>
            <span class="hero-chip">∿ EDA &amp; Stats</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1.1, 1])
        with col2:
            if st.button("🚀  Get Started — Upload Data", use_container_width=True):
                st.session_state["nav"] = "File Upload"
                st.rerun()

    else:
        df = st.session_state["clean_data"]
        num_cols = df.select_dtypes(include=["int64","float64","int32","float32"]).shape[1]
        cat_cols = df.select_dtypes(include=["object","category"]).shape[1]
        missing  = int(df.isnull().sum().sum())
        dups     = int(df.duplicated().sum())

        st.markdown(f"""
        <style>
        @keyframes rainbowFlow {{
          0%   {{ background-position: 0% center; }}
          100% {{ background-position: 200% center; }}
        }}
        .ds-rainbow {{
          background: linear-gradient(90deg,#ff0000,#ff6600,#ffcc00,#00ff88,#00cfff,#6600ff,#ff00cc,#ff0000);
          background-size: 300% auto;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: rainbowFlow 1.5s linear infinite;
          font-weight: 800;
          font-size: 1.25rem;
          letter-spacing: -.5px;
        }}
        </style>
        <div style="background:#0e1117;border:1px solid #1f2937;border-radius:14px;
                    padding:1.3rem 1.5rem;margin-bottom:.75rem;position:relative;overflow:hidden;">
          <div style="position:absolute;top:0;left:0;right:0;height:2px;
                      background:linear-gradient(90deg,#6366f1,#38bdf8,#4ade80);"></div>
          <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem;">
            <span style="color:#4ade80;font-size:.85rem;">●</span>
            <span class="ds-rainbow">{st.session_state.get("filename","dataset")}</span>
          </div>
          <div style="color:#6b7280;font-size:.8rem;">
            {df.shape[0]:,} rows &nbsp;·&nbsp; {df.shape[1]} columns &nbsp;·&nbsp; ready to explore
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(kpi_row_html([
            ("Rows",        f"{df.shape[0]:,}"),
            ("Columns",     df.shape[1]),
            ("Numeric",     num_cols),
            ("Categorical", cat_cols),
            ("Missing",     f"{missing:,}"),
            ("Duplicates",  dups),
        ]), unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("◎ Profile Data", use_container_width=True):
                st.session_state["nav"] = "Data Profiling"; st.rerun()
        with c2:
            if st.button("∿ EDA & Stats", use_container_width=True):
                st.session_state["nav"] = "EDA & Statistics"; st.rerun()
        with c3:
            if st.button("⚡ Dashboard", use_container_width=True):
                st.session_state["nav"] = "Dashboard Generator"; st.rerun()
        with c4:
            if st.button("▦ Chart Builder", use_container_width=True):
                st.session_state["nav"] = "Chart Builder"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Feature cards ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:.65rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
                color:#374151;margin-bottom:1.1rem;">Platform Features</div>
    """, unsafe_allow_html=True)

    features = [
        ("⬆", "Smart Upload",     "#f472b6", "CSV, Excel, JSON, Parquet with auto type detection."),
        ("◎", "Data Profiling",   "#fb923c", "Per-column stats, distributions, and quality scores."),
        ("✦", "Data Cleaning",    "#facc15", "Remove duplicates, fill nulls, cast types, filter rows."),
        ("∿", "EDA & Statistics", "#4ade80", "Correlations, distributions, hypothesis tests."),
        ("▦", "Chart Builder",    "#38bdf8", "Bar, scatter, pie, heatmap, violin — no code needed."),
        ("⚡", "Auto Dashboard",  "#a78bfa", "Auto-generate KPIs and smart charts from your data."),
        ("⏱", "Time Series",      "#f472b6", "Trend analysis, rolling averages, decomposition."),
        ("◈", "ML Insights",      "#38bdf8", "Clustering, anomaly detection, PCA, feature importance."),
        ("◑", "Forecasting",      "#4ade80", "ARIMA and exponential smoothing forecasts."),
        ("↓", "Export",           "#fb923c", "Download cleaned data as CSV with one click."),
    ]

    cols_per_row = 5
    for row_start in range(0, len(features), cols_per_row):
        row_features = features[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, (icon, title, color, desc) in enumerate(row_features):
            with cols[i]:
                st.markdown(f"""
                <div style="background:#0e1117;border:1px solid #1f2937;border-radius:12px;
                            padding:1.15rem 1rem;height:100%;position:relative;overflow:hidden;">
                  <div style="position:absolute;top:0;left:0;right:0;height:2px;
                              background:{color};opacity:.8;"></div>
                  <div style="font-size:1.45rem;margin-bottom:.55rem;">{icon}</div>
                  <div style="font-weight:700;color:#e8eaf6;margin-bottom:.35rem;
                              font-size:.86rem;">{title}</div>
                  <div style="color:#6b7280;font-size:.73rem;line-height:1.55;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📘 How It Works", "🚀 Roadmap", "💬 Support"])

    with tab1:
        st.markdown("""
        <div style="background:#0e1117;border:1px solid #1f2937;border-radius:12px;
                    padding:1.5rem;line-height:2;">
          <b style="color:#38bdf8;">✅ Workflow in 4 steps:</b><br><br>
          <b style="color:#e8eaf6;">1. Upload</b>
            <span style="color:#6b7280;"> — Drag and drop your CSV, Excel, JSON, or Parquet file.</span><br>
          <b style="color:#e8eaf6;">2. Profile &amp; Clean</b>
            <span style="color:#6b7280;"> — Inspect column types, handle missing values and duplicates.</span><br>
          <b style="color:#e8eaf6;">3. Explore &amp; Visualize</b>
            <span style="color:#6b7280;"> — Run EDA, build charts, and auto-generate dashboards.</span><br>
          <b style="color:#e8eaf6;">4. Model &amp; Export</b>
            <span style="color:#6b7280;"> — Apply ML insights, forecasting, and download your results.</span>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div style="background:#0e1117;border:1px solid #1f2937;border-radius:12px;
                    padding:1.5rem;line-height:2;">
          <b style="color:#a78bfa;">🌟 Coming Soon:</b><br><br>
          <span style="color:#6b7280;">
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
            st.markdown('<div style="color:#6b7280;margin-bottom:1rem;">Need help? Fill out the form below.</div>', unsafe_allow_html=True)
            name    = st.text_input("Your Name")
            email   = st.text_input("Your Email")
            message = st.text_area("Message", height=120)
            submitted = st.form_submit_button("Send Message")
            if submitted:
                if name and email and message:
                    st.success("✅ Thank you! Your message has been received.")
                else:
                    st.error("⚠️ Please fill in all fields before submitting.")
