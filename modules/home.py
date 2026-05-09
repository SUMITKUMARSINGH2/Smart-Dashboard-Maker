import streamlit as st


def home_page():
    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:#FFFFFF;border-radius:18px;padding:2rem 2.5rem;
                margin-bottom:1.5rem;border:1px solid #E2E8F0;
                box-shadow:0 4px 24px rgba(124,58,237,.07);'>
        <div style='font-size:.68rem;font-weight:800;letter-spacing:.12em;
                    text-transform:uppercase;color:#7C3AED;margin-bottom:.5rem;'>
            Professional Data Analytics
        </div>
        <h1 style='font-size:2.1rem;font-weight:800;color:#0F172A;
                   line-height:1.15;margin:0 0 .8rem;'>
            From Raw Data<br>
            <span style='background:linear-gradient(135deg,#7C3AED,#F43F5E);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;'>
                to Real Insights
            </span>
        </h1>
        <p style='color:#6B7280;font-size:.9rem;line-height:1.65;
                  max-width:560px;margin:0 0 1.2rem;'>
            Upload CSV, Excel, JSON or Parquet · Profile &amp; clean your data ·
            Build interactive charts · Run ML clustering and anomaly detection ·
            Export to HTML, Excel or Power BI.
        </p>
        <div style='display:flex;gap:.5rem;flex-wrap:wrap;'>
    """, unsafe_allow_html=True)

    badges = [
        ("#7C3AED", "#EDE9FE", "4+ File Formats"),
        ("#F43F5E", "#FFF1F2", "19+ Chart Types"),
        ("#059669", "#ECFDF5", "Power BI Export"),
        ("#D97706", "#FFFBEB", "Copy Chart Code"),
        ("#0EA5E9", "#F0F9FF", "ML Clustering"),
    ]
    tags = "".join(
        f"""<span style='background:{bg};color:{fg};border-radius:20px;
                   padding:.28rem .8rem;font-size:.74rem;font-weight:700;'>{label}</span>"""
        for fg, bg, label in badges
    )
    st.markdown(tags + "</div></div>", unsafe_allow_html=True)

    # ── Stats row ──────────────────────────────────────────────────────────────
    nums = [
        ("#7C3AED", "#F5F3FF", "19+", "Chart Types"),
        ("#F43F5E", "#FFF1F2", "8+",  "Clean Tools"),
        ("#059669", "#ECFDF5", "4",   "Export Formats"),
        ("#D97706", "#FFFBEB", "ML",  "Insights"),
    ]
    cols = st.columns(4)
    for col, (fg, bg, val, lbl) in zip(cols, nums):
        col.markdown(f"""
        <div style='background:{bg};border-radius:12px;padding:1rem 1.2rem;text-align:center;'>
            <div style='font-size:1.7rem;font-weight:800;color:{fg};'>{val}</div>
            <div style='font-size:.7rem;font-weight:700;color:{fg};opacity:.8;margin-top:2px;'>{lbl}</div>
        </div>""", unsafe_allow_html=True)

    # ── Feature grid ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style='margin:1.8rem 0 .8rem;'>
        <div style='font-size:.67rem;font-weight:800;letter-spacing:.1em;
                    text-transform:uppercase;color:#7C3AED;'>What's inside</div>
        <h2 style='font-size:1.3rem;font-weight:800;color:#0F172A;margin:.3rem 0 0;'>
            Ten powerful modules
        </h2>
        <div style='width:36px;height:3px;background:linear-gradient(90deg,#7C3AED,#F43F5E);
                    border-radius:2px;margin:.5rem 0;'></div>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("#7C3AED", "#F5F3FF", "Upload Data",
         "CSV, Excel, JSON, Parquet. Auto type detection, inline preview, quick summary stats."),
        ("#F43F5E", "#FFF1F2", "Data Profiling",
         "Full per-column profile: missing %, skewness, kurtosis, unique counts, memory usage."),
        ("#059669", "#ECFDF5", "Data Cleaning",
         "Remove duplicates, fill nulls (mean/median/mode/interpolate), outlier IQR & Z-Score removal."),
        ("#D97706", "#FFFBEB", "EDA & Statistics",
         "Seaborn correlation heatmaps, distribution plots, pair plots, t-test, ANOVA, chi-square."),
        ("#0EA5E9", "#F0F9FF", "Chart Builder",
         "19 Plotly chart types. Full parameter control. One-click HTML export + copy Python code."),
        ("#8B5CF6", "#F5F3FF", "Auto Dashboard",
         "Auto-generates KPI cards, correlation matrix, bar charts, box plots and pivot heatmaps."),
        ("#EC4899", "#FDF2F8", "Time Series",
         "Auto-detect dates. Trend lines, rolling averages, seasonality, growth rate analysis."),
        ("#14B8A6", "#F0FDFA", "ML Insights",
         "K-Means clustering, Isolation Forest anomaly detection, feature importance, PCA viz."),
        ("#F97316", "#FFF7ED", "Export & Reports",
         "CSV, Excel, JSON, Parquet. Chart HTML export. Power BI Excel + M Query + DAX bundle."),
    ]

    c1, c2, c3 = st.columns(3)
    cols_list = [c1, c2, c3]
    for i, (fg, bg, title, desc) in enumerate(features):
        cols_list[i % 3].markdown(f"""
        <div style='background:#FFFFFF;border-radius:12px;padding:1.1rem 1.3rem;
                    margin-bottom:.9rem;border:1px solid #F1F5F9;
                    box-shadow:0 1px 4px rgba(0,0,0,.04);
                    border-top:3px solid {fg};'>
            <div style='font-weight:800;color:#0F172A;font-size:.88rem;
                        margin-bottom:.35rem;'>{title}</div>
            <div style='color:#6B7280;font-size:.8rem;line-height:1.55;'>{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.info("**Get started** → click **Upload Data** in the sidebar to load your dataset.")

    # ── AdSense placeholder ────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:#F8FAFC;border:1px dashed #E2E8F0;border-radius:10px;
                padding:1rem;text-align:center;margin:1rem 0;
                color:#94A3B8;font-size:.78rem;'>
        <!-- Google AdSense ad unit goes here -->
    </div>
    """, unsafe_allow_html=True)
