import streamlit as st


def home_page():
    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='display:flex;gap:2rem;align-items:center;
                background:#FFFFFF;border-radius:20px;padding:2.5rem 3rem;
                margin-bottom:2rem;border:1px solid #EDE9FE;
                box-shadow:0 4px 24px rgba(124,58,237,.08);'>
        <div style='flex:1;'>
            <div style='font-size:.72rem;font-weight:800;letter-spacing:.12em;
                        text-transform:uppercase;color:#7C3AED;margin-bottom:.6rem;'>
                Professional Data Analytics
            </div>
            <h1 style='font-size:2.4rem;font-weight:800;color:#1C1917;
                       line-height:1.15;margin:0 0 .9rem;'>
                From Raw Data<br>
                <span style='background:linear-gradient(135deg,#7C3AED,#F43F5E);
                             -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
                to Real Insights
                </span>
            </h1>
            <p style='color:#6B7280;font-size:.95rem;line-height:1.65;
                      max-width:520px;margin:0 0 1.4rem;'>
                Upload CSV, Excel, JSON or Parquet · Profile &amp; clean your data ·
                Build interactive charts with Seaborn &amp; Plotly ·
                Run ML clustering and anomaly detection · Export to HTML, Excel or Power BI.
            </p>
            <div style='display:flex;gap:.6rem;flex-wrap:wrap;'>
    """, unsafe_allow_html=True)

    badges = [
        ("#7C3AED", "#EDE9FE", "4+ File Formats"),
        ("#F43F5E", "#FFF1F2", "19+ Chart Types"),
        ("#059669", "#ECFDF5", "Power BI Export"),
        ("#D97706", "#FFFBEB", "Copy Chart Code"),
        ("#0EA5E9", "#F0F9FF",  "ML Clustering"),
    ]
    tags = "".join(f"""<span style='background:{bg};color:{fg};border-radius:20px;
                       padding:.3rem .85rem;font-size:.75rem;font-weight:700;'>{label}</span>"""
                   for fg, bg, label in badges)
    st.markdown(tags + "</div></div>", unsafe_allow_html=True)

    # right side big number cluster
    st.markdown("""
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:1rem;min-width:240px;'>
    """, unsafe_allow_html=True)
    nums = [
        ("#7C3AED","#F5F3FF","19+","Chart Types"),
        ("#F43F5E","#FFF1F2","8+","Clean Tools"),
        ("#059669","#ECFDF5","4","Export Formats"),
        ("#D97706","#FFFBEB","ML","Insights"),
    ]
    for fg, bg, val, lbl in nums:
        st.markdown(f"""
        <div style='background:{bg};border-radius:14px;padding:1rem 1.2rem;text-align:center;'>
            <div style='font-size:1.8rem;font-weight:800;color:{fg};'>{val}</div>
            <div style='font-size:.72rem;font-weight:700;color:{fg};opacity:.8;margin-top:2px;'>{lbl}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Feature grid ─────────────────────────────────────────────────────
    st.markdown("""
    <div style='margin:2rem 0 .8rem;'>
        <div style='font-size:.7rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;
                    color:#7C3AED;'>What's inside</div>
        <h2 style='font-size:1.4rem;font-weight:800;color:#1C1917;margin:.3rem 0 0;'>
            Ten powerful modules
        </h2>
        <div style='width:40px;height:3px;background:linear-gradient(90deg,#7C3AED,#F43F5E);
                    border-radius:2px;margin:.6rem 0;'></div>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("#7C3AED","#F5F3FF","Upload Data",
         "CSV, Excel, JSON, Parquet. Auto type detection, inline preview, quick summary stats."),
        ("#F43F5E","#FFF1F2","Data Profiling",
         "Full per-column profile: missing %, skewness, kurtosis, unique counts, memory usage."),
        ("#059669","#ECFDF5","Data Cleaning",
         "Remove duplicates, fill nulls (mean/median/mode/interpolate), outlier IQR & Z-Score removal."),
        ("#D97706","#FFFBEB","EDA & Statistics",
         "Seaborn correlation heatmaps, distribution plots, pair plots, t-test, ANOVA, chi-square."),
        ("#0EA5E9","#F0F9FF","Chart Builder",
         "19 Plotly chart types. Full parameter control. One-click HTML export + copy Python code."),
        ("#8B5CF6","#F5F3FF","Auto Dashboard",
         "Auto-generates KPI cards, correlation matrix, bar charts, box plots and pivot heatmaps."),
        ("#EC4899","#FDF2F8","Time Series",
         "Auto-detect dates. Trend lines, rolling averages, seasonality, growth rate analysis."),
        ("#14B8A6","#F0FDFA","ML Insights",
         "K-Means clustering, Isolation Forest anomaly detection, feature importance, PCA viz."),
        ("#F97316","#FFF7ED","Export & Reports",
         "CSV, Excel, JSON, Parquet. Chart HTML export. Power BI Excel + M Query + DAX bundle."),
    ]

    cols = st.columns(3)
    for i, (fg, bg, title, desc) in enumerate(features):
        cols[i % 3].markdown(f"""
        <div style='background:#FFFFFF;border-radius:14px;padding:1.2rem 1.4rem;
                    margin-bottom:1rem;border:1px solid #F3F4F6;
                    box-shadow:0 1px 4px rgba(0,0,0,.04);
                    border-top:3px solid {fg};'>
            <div style='font-weight:800;color:#1C1917;font-size:.9rem;margin-bottom:.4rem;'>{title}</div>
            <div style='color:#6B7280;font-size:.81rem;line-height:1.55;'>{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.info("**Get started** → click **Upload Data** in the sidebar. All modules unlock once a dataset is loaded.")
