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
                <div style="background:linear-gradient(90deg,rgba(168,85,247,.12),rgba(0,212,255,.08));
                            border:1px solid rgba(168,85,247,.25);border-radius:10px;
                            padding:.65rem 1rem;margin-bottom:1rem;
                            display:flex;align-items:center;gap:.6rem;font-size:.83rem;color:#c4b5fd;">
                  <span style="font-size:1rem;">⟳</span>
                  <span>Flask loaded <b style="color:#f0f0ff;">{bridge_file}</b> ({bridge_rows:,} rows). Sync?</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"⟳  Sync \"{bridge_file}\" from Flask", use_container_width=False):
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
        @keyframes rainbow {
          0%   { color: #ff0000; text-shadow: 0 0 30px #ff000099, 0 0 60px #ff000044; }
          10%  { color: #ff6600; text-shadow: 0 0 30px #ff660099, 0 0 60px #ff660044; }
          20%  { color: #ffcc00; text-shadow: 0 0 30px #ffcc0099, 0 0 60px #ffcc0044; }
          30%  { color: #33ff00; text-shadow: 0 0 30px #33ff0099, 0 0 60px #33ff0044; }
          40%  { color: #00ffcc; text-shadow: 0 0 30px #00ffcc99, 0 0 60px #00ffcc44; }
          50%  { color: #0099ff; text-shadow: 0 0 30px #0099ff99, 0 0 60px #0099ff44; }
          60%  { color: #6600ff; text-shadow: 0 0 30px #6600ff99, 0 0 60px #6600ff44; }
          70%  { color: #cc00ff; text-shadow: 0 0 30px #cc00ff99, 0 0 60px #cc00ff44; }
          80%  { color: #ff0099; text-shadow: 0 0 30px #ff009999, 0 0 60px #ff009944; }
          90%  { color: #ff3333; text-shadow: 0 0 30px #ff333399, 0 0 60px #ff333344; }
          100% { color: #ff0000; text-shadow: 0 0 30px #ff000099, 0 0 60px #ff000044; }
        }
        @keyframes floatBadge {
          0%,100% { transform: translateY(0); }
          50%      { transform: translateY(-5px); }
        }
        @keyframes pulseGlow {
          0%,100% { box-shadow: 0 0 20px rgba(168,85,247,.3), 0 0 60px rgba(168,85,247,.1); }
          50%      { box-shadow: 0 0 40px rgba(168,85,247,.6), 0 0 80px rgba(168,85,247,.2); }
        }
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(24px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .hero-wrap {
          text-align: center;
          padding: 3.5rem 1rem 2.5rem;
          animation: fadeSlideUp .7s ease both;
        }
        .hero-badge {
          display: inline-flex; align-items: center; gap: .5rem;
          background: rgba(168,85,247,.12);
          border: 1px solid rgba(168,85,247,.35);
          border-radius: 999px;
          padding: .4rem 1.2rem;
          font-size: .8rem; font-weight: 600; color: #c4b5fd;
          margin-bottom: 1.8rem;
          animation: floatBadge 2.5s ease-in-out infinite;
        }
        .hero-title {
          font-size: clamp(2.6rem, 6vw, 4.2rem);
          font-weight: 900;
          line-height: 1.05;
          margin-bottom: .5rem;
          color: #f0f0ff;
          letter-spacing: -2px;
        }
        .hero-rainbow {
          animation: rainbow 1s linear infinite;
          display: block;
          font-size: clamp(2.6rem, 6vw, 4.2rem);
          font-weight: 900;
          letter-spacing: -2px;
          margin-bottom: 1.4rem;
        }
        .hero-sub {
          color: #8888aa;
          font-size: 1.05rem;
          max-width: 560px;
          margin: 0 auto 2.5rem;
          line-height: 1.75;
        }
        .hero-pills {
          display: flex; flex-wrap: wrap; justify-content: center; gap: .5rem;
          margin-bottom: 2rem;
        }
        .hero-pill {
          background: rgba(255,255,255,.05);
          border: 1px solid #2a2a3d;
          border-radius: 999px;
          padding: .3rem .9rem;
          font-size: .75rem; color: #8888aa;
        }
        </style>

        <div class="hero-wrap">
          <div class="hero-badge">✦ Advanced Data Analytics Platform</div>
          <div class="hero-title">Turn Raw Data Into</div>
          <span class="hero-rainbow">Powerful Insights</span>
          <p class="hero-sub">
            Upload any dataset — CSV, Excel, JSON, Parquet — and instantly
            explore, clean, visualize, and model your data with zero code required.
          </p>
          <div class="hero-pills">
            <span class="hero-pill">📊 CSV &amp; Excel</span>
            <span class="hero-pill">📁 JSON &amp; Parquet</span>
            <span class="hero-pill">🤖 ML Insights</span>
            <span class="hero-pill">📈 Auto Dashboard</span>
            <span class="hero-pill">⏱ Time Series</span>
            <span class="hero-pill">◑ Forecasting</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("🚀  Get Started — Upload Data", use_container_width=True):
                st.session_state["nav"] = "File Upload"
                st.rerun()

    else:
        df = st.session_state["clean_data"]
        import pandas as pd
        num_cols = df.select_dtypes(include=["int64","float64","int32","float32"]).shape[1]
        cat_cols = df.select_dtypes(include=["object","category"]).shape[1]
        missing  = int(df.isnull().sum().sum())
        dups     = int(df.duplicated().sum())

        st.markdown(f"""
        <style>
        @keyframes rainbow {{
          0%   {{ color: #ff0000; text-shadow: 0 0 30px #ff000099; }}
          16%  {{ color: #ff9900; text-shadow: 0 0 30px #ff990099; }}
          33%  {{ color: #ffff00; text-shadow: 0 0 30px #ffff0099; }}
          50%  {{ color: #00ff99; text-shadow: 0 0 30px #00ff9999; }}
          66%  {{ color: #0099ff; text-shadow: 0 0 30px #0099ff99; }}
          83%  {{ color: #cc00ff; text-shadow: 0 0 30px #cc00ff99; }}
          100% {{ color: #ff0000; text-shadow: 0 0 30px #ff000099; }}
        }}
        .loaded-title {{
          animation: rainbow 1s linear infinite;
          font-size: 1.6rem;
          font-weight: 900;
          letter-spacing: -1px;
        }}
        </style>
        <div style="background:linear-gradient(135deg,rgba(168,85,247,.08),rgba(0,212,255,.05));
                    border:1px solid rgba(168,85,247,.2);border-radius:14px;
                    padding:1.4rem 1.6rem;margin-bottom:.5rem;">
          <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.3rem;">
            <span style="color:#6bcb77;font-size:.9rem;">●</span>
            <span class="loaded-title">{st.session_state.get("filename","dataset")}</span>
          </div>
          <div style="color:#8888aa;font-size:.82rem;">
            Dataset loaded · {df.shape[0]:,} rows · {df.shape[1]} columns · ready to explore
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
    <div style="font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
                color:#55557a;margin-bottom:1.2rem;">Platform Features</div>
    """, unsafe_allow_html=True)

    features = [
        ("⬆", "Smart Upload",       "#ff6b6b", "CSV, Excel, JSON, Parquet with auto type detection."),
        ("◎", "Data Profiling",     "#ffd93d", "Per-column stats, distributions, and quality scores."),
        ("✦", "Data Cleaning",      "#6bcb77", "Remove duplicates, fill nulls, cast types, filter rows."),
        ("∿", "EDA & Statistics",   "#4d96ff", "Correlations, distributions, hypothesis tests."),
        ("▦", "Chart Builder",      "#c77dff", "Bar, scatter, pie, heatmap, violin — no code needed."),
        ("⚡", "Auto Dashboard",    "#ff9f1c", "Auto-generate KPIs and smart charts from your data."),
        ("⏱", "Time Series",        "#ff6b6b", "Trend analysis, rolling averages, decomposition."),
        ("◈", "ML Insights",        "#4d96ff", "Clustering, anomaly detection, PCA, feature importance."),
        ("◑", "Forecasting",        "#6bcb77", "ARIMA and exponential smoothing forecasts."),
        ("↓", "Export",             "#c77dff", "Download cleaned data as CSV with one click."),
    ]

    cols_per_row = 5
    for row_start in range(0, len(features), cols_per_row):
        row_features = features[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, (icon, title, color, desc) in enumerate(row_features):
            with cols[i]:
                st.markdown(f"""
                <div style="background:#12121a;border:1px solid #2a2a3d;border-radius:14px;
                            padding:1.25rem 1rem;height:100%;transition:all .25s;
                            position:relative;overflow:hidden;">
                  <div style="position:absolute;top:0;left:0;right:0;height:3px;
                              background:linear-gradient(90deg,{color},{color}66);"></div>
                  <div style="font-size:1.6rem;margin-bottom:.65rem;">{icon}</div>
                  <div style="font-weight:700;color:#f0f0ff;margin-bottom:.4rem;
                              font-size:.88rem;">{title}</div>
                  <div style="color:#8888aa;font-size:.75rem;line-height:1.55;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📘 How It Works", "🚀 Roadmap", "💬 Support"])

    with tab1:
        st.markdown("""
        <div style="background:#12121a;border:1px solid #2a2a3d;border-radius:14px;
                    padding:1.6rem;line-height:1.9;">
          <b style="color:#a855f7;">✅ Workflow in 4 steps:</b><br><br>
          <b style="color:#f0f0ff;">1. Upload</b>
            <span style="color:#8888aa;"> — Drag and drop your CSV, Excel, JSON, or Parquet file.</span><br>
          <b style="color:#f0f0ff;">2. Profile &amp; Clean</b>
            <span style="color:#8888aa;"> — Inspect column types, handle missing values and duplicates.</span><br>
          <b style="color:#f0f0ff;">3. Explore &amp; Visualize</b>
            <span style="color:#8888aa;"> — Run EDA, build charts, and auto-generate dashboards.</span><br>
          <b style="color:#f0f0ff;">4. Model &amp; Export</b>
            <span style="color:#8888aa;"> — Apply ML insights, forecasting, and download your results.</span>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div style="background:#12121a;border:1px solid #2a2a3d;border-radius:14px;
                    padding:1.6rem;line-height:1.9;">
          <b style="color:#c77dff;">🌟 Coming Soon:</b><br><br>
          <span style="color:#8888aa;">
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
            st.markdown('<div style="color:#8888aa;margin-bottom:1rem;">Need help? Fill out the form below.</div>', unsafe_allow_html=True)
            name    = st.text_input("Your Name")
            email   = st.text_input("Your Email")
            message = st.text_area("Message", height=120)
            submitted = st.form_submit_button("Send Message")
            if submitted:
                if name and email and message:
                    st.success("✅ Thank you! Your message has been received.")
                else:
                    st.error("⚠️ Please fill in all fields before submitting.")
