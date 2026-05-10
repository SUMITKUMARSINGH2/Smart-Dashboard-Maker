import streamlit as st
from styles import DARK_CSS, SIDEBAR_CSS, section_header, kpi_row_html, badge
from shared_store import load_shared, get_meta as bridge_meta, bridge_exists

RAINBOW_FLOW_CSS = """
<style>
@keyframes rainbowFlow {
  0%   { background-position: 0% center; }
  100% { background-position: 200% center; }
}
@keyframes fadeUp {
  from { opacity:0; transform:translateY(28px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes bobble {
  0%,100% { transform:translateY(0); }
  50%      { transform:translateY(-5px); }
}
@keyframes glowPulse {
  0%,100% { opacity:.4; transform:scale(1); }
  50%      { opacity:.7; transform:scale(1.05); }
}

/* Glowing blobs behind hero */
.hero-glow-1 {
  position:absolute; top:-80px; left:50%; transform:translateX(-50%);
  width:500px; height:300px;
  background: radial-gradient(ellipse, rgba(99,102,241,.18) 0%, transparent 70%);
  pointer-events:none;
  animation: glowPulse 4s ease-in-out infinite;
}
.hero-glow-2 {
  position:absolute; top:0; left:10%;
  width:250px; height:250px;
  background: radial-gradient(circle, rgba(168,85,247,.12) 0%, transparent 70%);
  pointer-events:none;
}
.hero-glow-3 {
  position:absolute; top:0; right:10%;
  width:250px; height:250px;
  background: radial-gradient(circle, rgba(56,189,248,.1) 0%, transparent 70%);
  pointer-events:none;
}

.hero-wrap {
  position:relative;
  text-align:center;
  padding:5rem 1rem 3rem;
  animation: fadeUp .65s cubic-bezier(.22,.68,0,1.2) both;
  overflow:hidden;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: .5rem;
  background: rgba(129,140,248,.1);
  border: 1px solid rgba(129,140,248,.25);
  border-radius: 999px;
  padding: .35rem 1rem .35rem .6rem;
  font-size: .78rem;
  font-weight: 600;
  color: #818cf8;
  margin-bottom: 2.2rem;
  animation: bobble 3.5s ease-in-out infinite;
  letter-spacing: .03em;
}
.hero-eyebrow-dot {
  width:6px; height:6px;
  background: linear-gradient(135deg,#6366f1,#a855f7);
  border-radius:50%;
  box-shadow: 0 0 8px rgba(99,102,241,.8);
}

.hero-title-top {
  font-size: clamp(2.2rem, 5vw, 3.6rem);
  font-weight: 900;
  color: #f1f2f6;
  line-height: 1.05;
  letter-spacing: -2.5px;
  margin-bottom: .1rem;
}

.hero-title-rainbow {
  font-size: clamp(2.2rem, 5vw, 3.6rem);
  font-weight: 900;
  letter-spacing: -2.5px;
  line-height: 1.15;
  margin-bottom: 1.8rem;
  background: linear-gradient(
    90deg,
    #ff0000 0%, #ff6600 12%, #ffcc00 25%,
    #00ff88 37%, #00cfff 50%, #6600ff 62%,
    #ff00cc 75%, #ff0000 87%, #ff6600 100%
  );
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: rainbowFlow 1.8s linear infinite;
  display: block;
}

.hero-sub {
  color: #7c7f96;
  font-size: 1rem;
  max-width: 500px;
  margin: 0 auto 2.5rem;
  line-height: 1.8;
  font-weight: 400;
}

/* Feature chips row */
.chip-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: .4rem;
  margin-bottom: 2.8rem;
}
.chip {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 999px;
  padding: .28rem .85rem;
  font-size: .72rem;
  color: #7c7f96;
  font-weight: 500;
  letter-spacing: .02em;
}

/* Stats row */
.stats-strip {
  display: flex;
  justify-content: center;
  gap: 3rem;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255,255,255,.06);
}
.stat-item { text-align:center; }
.stat-num {
  font-size: 1.6rem;
  font-weight: 800;
  background: linear-gradient(135deg,#818cf8,#a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.stat-label { font-size:.7rem; color:#3d3f52; text-transform:uppercase; letter-spacing:.1em; margin-top:2px; }
</style>
"""


def home_page():
    st.markdown(DARK_CSS + SIDEBAR_CSS, unsafe_allow_html=True)
    st.markdown(RAINBOW_FLOW_CSS, unsafe_allow_html=True)

    has_data = "clean_data" in st.session_state and st.session_state["clean_data"] is not None

    # Bridge sync banner
    if bridge_exists():
        meta = bridge_meta()
        if meta:
            session_file = st.session_state.get("filename", "")
            bridge_file  = meta.get("filename", "")
            if meta.get("source") == "flask" and bridge_file != session_file:
                st.markdown(f"""
                <div style="background:rgba(129,140,248,.07);border:1px solid rgba(129,140,248,.2);
                            border-radius:10px;padding:.6rem 1rem;margin-bottom:1rem;
                            display:flex;align-items:center;gap:.6rem;font-size:.82rem;color:#a5b4fc;">
                  <span>⟳</span>
                  Flask loaded <b style="color:#f1f2f6;">{bridge_file}</b> ({meta.get('rows',0):,} rows).
                </div>
                """, unsafe_allow_html=True)
                if st.button("⟳  Sync from Flask"):
                    df, _ = load_shared()
                    if df is not None:
                        st.session_state.update({"raw_data": df.copy(), "clean_data": df.copy(), "filename": bridge_file})
                        st.rerun()

    # ── Hero / Dashboard state ─────────────────────────────────────────────
    if not has_data:
        st.markdown("""
        <div class="hero-wrap">
          <div class="hero-glow-1"></div>
          <div class="hero-glow-2"></div>
          <div class="hero-glow-3"></div>

          <div class="hero-eyebrow">
            <span class="hero-eyebrow-dot"></span>
            Advanced Data Analytics Platform
          </div>

          <div class="hero-title-top">Turn Raw Data Into</div>
          <span class="hero-title-rainbow">Powerful Insights</span>

          <p class="hero-sub">
            Upload any dataset — CSV, Excel, JSON, Parquet — and instantly
            explore, clean, visualize, and model your data. Zero code required.
          </p>

          <div class="chip-row">
            <span class="chip">📊 CSV &amp; Excel</span>
            <span class="chip">📁 JSON &amp; Parquet</span>
            <span class="chip">🤖 ML Insights</span>
            <span class="chip">📈 Auto Dashboard</span>
            <span class="chip">⏱ Time Series</span>
            <span class="chip">◑ Forecasting</span>
            <span class="chip">✦ Data Cleaning</span>
            <span class="chip">∿ EDA &amp; Stats</span>
          </div>

          <div class="stats-strip">
            <div class="stat-item">
              <div class="stat-num">8+</div>
              <div class="stat-label">Analysis Tools</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">5</div>
              <div class="stat-label">File Formats</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">∞</div>
              <div class="stat-label">Rows Supported</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">0</div>
              <div class="stat-label">Code Required</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("🚀  Get Started — Upload Data", use_container_width=True):
                st.session_state["nav"] = "File Upload"
                st.rerun()

    else:
        df = st.session_state["clean_data"]
        fname = st.session_state.get("filename", "dataset")
        num_cols = df.select_dtypes(include=["int64","float64","int32","float32"]).shape[1]
        cat_cols = df.select_dtypes(include=["object","category"]).shape[1]
        missing  = int(df.isnull().sum().sum())
        dups     = int(df.duplicated().sum())

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(99,102,241,.08),rgba(168,85,247,.05));
                    border:1px solid rgba(129,140,248,.2);border-radius:16px;
                    padding:1.4rem 1.6rem;margin-bottom:1rem;position:relative;overflow:hidden;">
          <div style="position:absolute;top:0;left:0;right:0;height:2px;
                      background:linear-gradient(90deg,#6366f1,#a855f7,#38bdf8);"></div>
          <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem;">
            <span style="display:inline-block;width:8px;height:8px;background:#4ade80;
                         border-radius:50%;box-shadow:0 0 8px #4ade80;"></span>
            <span style="font-weight:800;font-size:1.1rem;
                         background:linear-gradient(90deg,#ff0000,#ff6600,#ffcc00,#00ff88,#00cfff,#6600ff,#ff00cc,#ff0000);
                         background-size:200% auto;
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
                         animation:rainbowFlow 1.8s linear infinite;">{fname}</span>
          </div>
          <div style="color:#7c7f96;font-size:.8rem;">
            {df.shape[0]:,} rows &nbsp;·&nbsp; {df.shape[1]} columns &nbsp;·&nbsp; dataset loaded
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
        for col, label, nav in [
            (c1, "◎ Profile",    "Data Profiling"),
            (c2, "∿ EDA",        "EDA & Statistics"),
            (c3, "⚡ Dashboard", "Dashboard Generator"),
            (c4, "▦ Charts",     "Chart Builder"),
        ]:
            with col:
                if st.button(label, use_container_width=True):
                    st.session_state["nav"] = nav; st.rerun()

    # ── Feature grid ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:1.25rem;">
      <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(129,140,248,.3),transparent);"></div>
      <div style="font-size:.65rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#3d3f52;">
        Everything you need
      </div>
      <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(129,140,248,.3));"></div>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("⬆", "Smart Upload",     "#818cf8", "rgba(129,140,248,.06)", "CSV, Excel, JSON, Parquet with auto type detection."),
        ("◎", "Data Profiling",   "#f472b6", "rgba(244,114,182,.06)", "Per-column stats, distributions, quality scores."),
        ("✦", "Data Cleaning",    "#fbbf24", "rgba(251,191,36,.06)",  "Remove duplicates, fill nulls, cast types, filter rows."),
        ("∿", "EDA & Statistics", "#4ade80", "rgba(74,222,128,.06)",  "Correlations, distributions, hypothesis tests."),
        ("▦", "Chart Builder",    "#38bdf8", "rgba(56,189,248,.06)",  "Bar, scatter, pie, heatmap, violin — drag & drop."),
        ("⚡", "Auto Dashboard",  "#a855f7", "rgba(168,85,247,.06)",  "Auto-generate KPIs and smart charts from data."),
        ("⏱", "Time Series",      "#f472b6", "rgba(244,114,182,.06)", "Trend analysis, rolling averages, decomposition."),
        ("◈", "ML Insights",      "#38bdf8", "rgba(56,189,248,.06)",  "Clustering, anomaly detection, PCA, importance."),
        ("◑", "Forecasting",      "#4ade80", "rgba(74,222,128,.06)",  "ARIMA and exponential smoothing forecasts."),
        ("↓", "Export",           "#fbbf24", "rgba(251,191,36,.06)",  "Download cleaned data and reports instantly."),
    ]

    cols_per_row = 5
    for row_start in range(0, len(features), cols_per_row):
        row = features[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, (icon, title, color, bg, desc) in enumerate(row):
            with cols[i]:
                st.markdown(f"""
                <div style="background:{bg};border:1px solid rgba(255,255,255,.06);
                            border-radius:14px;padding:1.2rem 1rem;height:100%;
                            position:relative;overflow:hidden;transition:all .2s;">
                  <div style="position:absolute;top:0;left:0;right:0;height:2px;
                              background:{color};opacity:.5;"></div>
                  <div style="font-size:1.5rem;margin-bottom:.6rem;
                              filter:drop-shadow(0 0 6px {color}66);">{icon}</div>
                  <div style="font-weight:700;color:#f1f2f6;margin-bottom:.35rem;
                              font-size:.86rem;letter-spacing:-.2px;">{title}</div>
                  <div style="color:#7c7f96;font-size:.72rem;line-height:1.55;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📘 How It Works", "🚀 Roadmap", "💬 Support"])

    with tab1:
        st.markdown("""
        <div style="background:rgba(129,140,248,.05);border:1px solid rgba(129,140,248,.15);
                    border-radius:14px;padding:1.6rem;line-height:2;">
          <b style="color:#818cf8;">✅ 4 steps to insights:</b><br><br>
          <b style="color:#f1f2f6;">1. Upload</b>
            <span style="color:#7c7f96;"> — Drop your CSV, Excel, JSON, or Parquet file.</span><br>
          <b style="color:#f1f2f6;">2. Profile &amp; Clean</b>
            <span style="color:#7c7f96;"> — Inspect types, handle missing values and duplicates.</span><br>
          <b style="color:#f1f2f6;">3. Explore &amp; Visualize</b>
            <span style="color:#7c7f96;"> — Run EDA, build charts, auto-generate dashboards.</span><br>
          <b style="color:#f1f2f6;">4. Model &amp; Export</b>
            <span style="color:#7c7f96;"> — Apply ML insights, forecasting, download results.</span>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div style="background:rgba(168,85,247,.05);border:1px solid rgba(168,85,247,.15);
                    border-radius:14px;padding:1.6rem;line-height:2;">
          <b style="color:#a855f7;">🌟 Coming Soon:</b><br><br>
          <span style="color:#7c7f96;">
            🤖 AutoML with model comparison &amp; leaderboard<br>
            ⏳ Advanced time series forecasting (Prophet)<br>
            📈 Smart chart recommendations via AI<br>
            🖼️ Dashboard templates library<br>
            ☁️ Cloud storage and live data connectors<br>
            👥 Collaboration, sharing and access control
          </span>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        with st.form("support_form", clear_on_submit=True):
            st.markdown('<div style="color:#7c7f96;margin-bottom:1rem;font-size:.88rem;">Have a question or issue? Send us a message.</div>', unsafe_allow_html=True)
            name    = st.text_input("Your Name")
            email   = st.text_input("Your Email")
            message = st.text_area("Message", height=110)
            if st.form_submit_button("Send Message"):
                if name and email and message:
                    st.success("✅ Message received — thank you!")
                else:
                    st.error("⚠️ Please fill in all fields.")
