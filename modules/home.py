import streamlit as st


def home_page():
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 60%,#0EA5E9 100%);
                border-radius:14px;padding:2.5rem 2.8rem;margin-bottom:2rem;'>
        <div style='display:flex;align-items:flex-start;gap:1.5rem;'>
            <div style='flex:1;'>
                <div style='color:#0EA5E9;font-size:0.75rem;font-weight:600;text-transform:uppercase;
                            letter-spacing:.1em;margin-bottom:.6rem;'>Professional Data Analytics</div>
                <h1 style='color:#F8FAFC;margin:0;font-size:2.2rem;font-weight:800;line-height:1.2;'>
                    Turn Raw Data Into<br>Actionable Insights
                </h1>
                <p style='color:#94A3B8;margin:0.8rem 0 0;font-size:1rem;line-height:1.6;max-width:500px;'>
                    Upload any dataset, clean it, explore patterns with Seaborn & Plotly,
                    build interactive charts, and export to HTML, Excel, or Power BI — all without writing code.
                </p>
                <div style='display:flex;gap:0.7rem;margin-top:1.4rem;flex-wrap:wrap;'>
                    <span style='background:rgba(14,165,233,0.2);color:#38BDF8;border:1px solid rgba(14,165,233,0.3);
                                 border-radius:20px;padding:0.3rem 0.9rem;font-size:0.78rem;font-weight:500;'>CSV &amp; Excel</span>
                    <span style='background:rgba(245,158,11,0.2);color:#FCD34D;border:1px solid rgba(245,158,11,0.3);
                                 border-radius:20px;padding:0.3rem 0.9rem;font-size:0.78rem;font-weight:500;'>JSON &amp; Parquet</span>
                    <span style='background:rgba(16,185,129,0.2);color:#6EE7B7;border:1px solid rgba(16,185,129,0.3);
                                 border-radius:20px;padding:0.3rem 0.9rem;font-size:0.78rem;font-weight:500;'>Power BI Export</span>
                    <span style='background:rgba(139,92,246,0.2);color:#C4B5FD;border:1px solid rgba(139,92,246,0.3);
                                 border-radius:20px;padding:0.3rem 0.9rem;font-size:0.78rem;font-weight:500;'>Copy Chart Code</span>
                </div>
            </div>
            <div style='font-size:6rem;opacity:0.15;user-select:none;'>📊</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    stats = [
        ("#0EA5E9", "4+", "File Formats", "CSV, Excel, JSON, Parquet"),
        ("#F59E0B", "19+", "Chart Types", "Bar, Scatter, Treemap, Sankey…"),
        ("#10B981", "8+", "Cleaning Tools", "Outlier detection, imputation…"),
        ("#8B5CF6", "3", "Export Targets", "HTML, Excel, Power BI"),
    ]
    for col, (color, val, label, sub) in zip(cols, stats):
        col.markdown(f"""
        <div class="stat-card" style="border-top-color:{color};">
            <div style="font-size:2rem;font-weight:800;color:{color};line-height:1">{val}</div>
            <div style="font-weight:600;color:#0F172A;margin-top:6px;font-size:0.9rem">{label}</div>
            <div style="color:#94A3B8;font-size:0.76rem;margin-top:3px">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='page-header'><h2>What You Can Do</h2><p>Eight powerful modules, zero code required</p></div>", unsafe_allow_html=True)

    features = [
        ("#0EA5E9", "Upload Data",       "Drop a CSV, Excel, JSON or Parquet file. Auto-detects types, previews rows, shows quick stats."),
        ("#F59E0B", "Data Profiling",    "Per-column stats: missing %, skewness, kurtosis, unique counts, memory. Missing-value bar chart."),
        ("#EF4444", "Data Cleaning",     "Remove duplicates, fill nulls (mean/median/mode/interpolate), detect and remove outliers via IQR or Z-Score."),
        ("#10B981", "EDA & Statistics",  "Seaborn correlation heatmaps, distribution plots, pair plots, and hypothesis tests (t-test, ANOVA, Chi-square)."),
        ("#8B5CF6", "Chart Builder",     "19 Plotly chart types — bar, scatter, treemap, sunburst, violin, funnel and more. Copy the Python code for any chart."),
        ("#0EA5E9", "Auto Dashboard",    "One click generates KPI cards, correlation matrix, distribution charts, and pivot heatmaps automatically."),
        ("#F59E0B", "Time Series",       "Auto-detect date columns, trend lines, rolling averages, periodicity breakdowns, and growth rate analysis."),
        ("#10B981", "Export & Reports",  "Download data as CSV/Excel/JSON. Export charts as HTML. Generate full data reports. Export Power BI-ready files + M Query scripts."),
    ]

    c1, c2 = st.columns(2)
    for i, (color, title, desc) in enumerate(features):
        target = c1 if i % 2 == 0 else c2
        target.markdown(f"""
        <div style='background:#FFFFFF;border-radius:10px;padding:1rem 1.3rem;
                    margin-bottom:0.8rem;box-shadow:0 1px 4px rgba(0,0,0,0.05);
                    border-left:4px solid {color};display:flex;gap:1rem;align-items:flex-start;'>
            <div style='flex:1;'>
                <div style='font-weight:700;color:#0F172A;font-size:0.9rem;margin-bottom:3px'>{title}</div>
                <div style='color:#64748B;font-size:0.82rem;line-height:1.5'>{desc}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("**Getting started:** Click **Upload Data** in the sidebar to load your dataset. All other modules unlock automatically once a dataset is loaded.")

    with st.expander("Supported file formats"):
        st.markdown("""
        | Format | Extension | Notes |
        |--------|-----------|-------|
        | Comma-Separated Values | `.csv` | Auto-detects comma or semicolon delimiter |
        | Excel Workbook | `.xlsx`, `.xls` | Multi-sheet support with sheet picker |
        | JSON | `.json` | Records, split, and index orientations |
        | Parquet | `.parquet` | High-performance columnar format |
        """)
